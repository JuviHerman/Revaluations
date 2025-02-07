from abc import abstractmethod

import pandas as pd
import numpy as np
import cvxpy as cvx
import matplotlib.pyplot as plt
from cvxpy import Expression

from const import RNPD_EQUATION_POLY_DEGREE, CONVEX_EPSILON_BETWEEN_GROUPS, LAMBDA_REG
from typing import List, Optional, Dict


class RnpdEquation:

    def __init__(self,
                 data: pd.DataFrame,
                 month: str,
                 poly_degree: int = RNPD_EQUATION_POLY_DEGREE):
        # data consists of columns ['group_index','duration_index','rnpd']
        self.data: pd.DataFrame = data
        self.month: str = month
        self.poly_degree: int = poly_degree
        self.groups: Optional[Dict[int, pd.DataFrame]] = {
            int(group): data[data['group_index']==group].set_index('group_index')
            for group in sorted(data['group_index'].unique())
        }
        self.coefficients = None

    @property
    def __name__(self):
        return self.month

    def __str__(self):
        return f"RnpdEquation({self.month})"

    def __repr__(self):
        return f"RnpdEquation(month='{self.month}')"


    def fit_polynomial_regression(self, epsilon=CONVEX_EPSILON_BETWEEN_GROUPS):
        # Define variables for polynomial coefficients
        degree = self.poly_degree
        coefficients = {group: cvx.Variable(degree + 1) for group in sorted(self.groups.keys())}

        # Polynomial function
        poly = lambda coef, duration: sum([coef[i] * duration ** i for i in range(degree + 1)])
        # Second derivative function
        second_derivative = lambda coef, x: sum([i * (i - 1) * coef[i] * x ** (i - 2) for i in range(2, degree + 1)])
        
        # Total error in cvx terms
        total_data_error = []
        regularization_terms = []
        for group in sorted(self.groups.keys()):

            # Calculate the error terms (L1 norm) for each group
            total_data_error.append(cvx.norm1(self.groups[group]['rnpd'].values -
                                    poly(coefficients[group], self.groups[group]['duration_index'].values))
                          )
            # L1 norm of the coefficient vector
            regularization_terms.append(cvx.norm1(coefficients[group]))

        total_error: Expression = cvx.sum(total_data_error) + cvx.sum(LAMBDA_REG * sum(regularization_terms))

        # Constraints for non-intersecting lines
        x_vals = np.linspace(0, 10, 100)
        constraints = []

        sorted_groups = sorted(self.groups.keys())
        for i in range(len(sorted_groups) - 1):
            group_current, group_next = sorted_groups[i], sorted_groups[i + 1]
            for x in x_vals:
                constraints.append(poly(coefficients[group_next], x) - poly(coefficients[group_current], x) >= epsilon)

        for group in sorted_groups:
            for x in x_vals:
                # Constraints to ensure RNPD is between 0 and 1
                constraints.append(poly(coefficients[group], x) <= 1)
                constraints.append(poly(coefficients[group], x) >= 0)
                # Second derivative >= 0
                constraints.append(second_derivative(coefficients[group], x) >= 0)

        # Solve the problem
        problem = cvx.Problem(cvx.Minimize(total_error), constraints)
        problem.solve()

        if problem.status in ["optimal", "optimal_inaccurate"]:
            self.coeffs = {group: coefficients[group].value for group in sorted_groups}
        else:
            raise Exception("Optimization failed")

    def get_matching_group(self, duration: float, rnpd: float) -> int:
        if self.coeffs is None:
            raise ValueError("Coefficients are not computed. Please run fit_polynomial_regression first.")

        closest_group = [
            abs(sum([self.coeffs[group][i] * duration ** i for i in range(len(self.coeffs[group]))]) - rnpd)
            for group in self.groups
        ]
        return np.argmin(closest_group) + 1


    def plot_graphs(self, month):
        if self.coeffs is None:
            raise ValueError("Coefficients are not computed. Please run fit_polynomial_regression first.")

        x_vals = np.linspace(0, 10, 100)

        plt.figure(figsize=(10, 6))

        # Plotting each polynomial for each group
        for group in sorted(self.groups.keys()):
            poly_vals = sum([self.coeffs[group][i] * x_vals ** i for i in range(self.poly_degree + 1)])
            plt.plot(x_vals, poly_vals, label=f'Group {group}')

        plt.ylabel('RNPD')
        plt.xlabel('Duration Index')
        plt.title(f'{month} - Polynomial Regression for Risk Groups')
        plt.legend(loc='upper right')
        plt.show()



