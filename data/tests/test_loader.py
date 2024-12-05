from data.data_loader import *
import pandas as pd
import matplotlib.pyplot as plt
import pickle

# loader = Loader()
# loader.load_ranked_data()
# with open('data.pkl', 'wb') as f:
#     pickle.dump(loader, f)
#

with open('data.pkl', 'rb') as f:
    loader = pickle.load(f)

print(loader.secs.shape)
if loader.is_loading_successful:
    loader.add_prospectus_data()
    if loader.is_prospectus_updated:
        print(loader.secs.shape)
        print(loader.secs[['GuaranteeID','NegativePledgeID','SeniorityID']].value_counts())
        loader.add_liquidity_premium()
        if loader.is_liquidity_calculated and loader.is_net_hazard_rate_updated:
            print(loader.secs.shape)
            print(loader.secs[['liquidity_premium_ami','Net Hazard Rate']].describe())
            # loader.build_full_dataset()
            # loader.calculate_rnpd()


