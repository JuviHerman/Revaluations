Revaluations: Dynamic Security Bond Risk Assessment

Overview

This project creates and maintains a predictive model for security bonds, employing polynomial functions and structured risk classes to assess security bonds’ risk dynamically. Using a convex optimization approach, it generates non-intersecting polynomial equations that form 12 distinct risk classes. These classes are designed to preemptively refine risk predictions based on market data, helping detect potential risk changes before external rating systems provide updated rankings.

Features

	•	Non-Intersecting Risk Classes: Generates 12 polynomial equations that define non-intersecting risk boundaries, each representing a unique risk class.
	•	Dynamic Learning from Market Data: The model processes concurrent market data to refine its predictions, adapting to new information to enhance risk assessment accuracy.
	•	Automated Monthly Model Updates: Each month, new equations are generated, allowing the system to update its predictions based on the latest market data.
	•	Convex Optimization: Ensures polynomial curves for each risk class do not intersect, maintaining clear risk differentiation between classes.
	•	Risk Prediction: Provides preemptive risk predictions based on current market conditions, aiding in timely decision-making.

Project Structure

	•	convex_handler.py: Manages the loading, processing, and prediction of monthly market data, integrating with ModelData to update and apply risk models.
	•	data_classes.py: Defines data structures, such as Sample, Duration, and M, to store market data and organize it into distinct groups for modeling.
	•	model_class.py: Implements ModelData, which builds and maintains the 12 risk classes, loading new data and fitting polynomial models.
	•	convex_class.py: Contains RnpdEquation, which handles polynomial regression with convex optimization to enforce non-intersecting risk functions.
	•	const.py: Stores constant values for configuration, such as required samples per class, polynomial degree, and data validation columns.

Usage

	1.	Setup: Ensure dependencies are installed, including pandas, numpy, cvxpy, and matplotlib.
	2.	Load and Train Monthly Models: Use convex_handler.py to load market data, fit polynomial models, and save monthly predictions.

    3.	Run Risk Predictions: predict function in convex_handler.py applies the latest model to provide risk predictions based on current market data.
	4.	Plot Results: Use plot_graphs in convex_class.py to visualize polynomial curves for each risk class.

Dependencies

	•	Python 3.x
	•	pandas, numpy, cvxpy, matplotlib

License

This project is licensed under the MIT License. See the LICENSE file for details.