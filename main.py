import datetime

import numpy as np
from runModel import run_model
import pandas as pd
import random as rand

if __name__ == '__main__':
    attack_kind = 0
    dry_run = False
    rand.seed(311)
    attack_start = 5
    print('Start Simulation for attack kind:', attack_kind)

    for prebunk in np.arange(0, 1.1, 0.1):
        prob_prebunk = round(prebunk, 1)

        for immune in np.arange(0, 1.1, 0.1):
            prob_immune = round(immune, 1)

            store_end_result = pd.DataFrame()
            store_shares_result = pd.DataFrame()
            store_status_result = pd.DataFrame()

            for indifferent in np.arange(0, 1.1, 0.1):
                prob_share_indifferent = round(indifferent, 1)
                print('Prebunk:', prebunk, 'Immune:', immune, 'Indifferent:', prob_share_indifferent)
                for disinfo in np.arange(0, 1.1, 0.1):
                    prob_share_disinfo = round(disinfo, 1)
                    print('Disinfo:', prob_share_disinfo)
                    for facts in np.arange(0, 1.1, 0.1):
                        prob_share_facts = round(facts, 1)

                        end_result_s = []
                        end_result_i = []
                        end_result_r = []

                        shares_result_s = []
                        shares_result_i = []
                        shares_result_r = []

                        status_result_s = []
                        status_result_i = []
                        status_result_r = []
                        status_result_ar = []
                        status_result_ui = []

                        formatted_attack_kind = str(attack_kind).replace('.', '_')
                        formatted_prob_prebunk = str(prob_prebunk).replace('.', '_')
                        formatted_prob_immune = str(prob_immune).replace('.', '_')



                        # Start the model
                        for _ in range(100):
                            end_result, shares_result, status_result = run_model(
                                pop_size=100,
                                n_ticks=100,
                                n_friends=5,
                                n_add=5,
                                prob_share_indifferent=prob_share_indifferent,
                                prob_share_disinfo=prob_share_disinfo,
                                prob_share_facts=prob_share_facts,

                                attack_start=attack_start,
                                attack_kind=attack_kind,
                                dark_quantile=.75,

                                prob_prebunk=prob_prebunk,
                                prob_immune=prob_immune,
                                draw = False,
                                verbose=False,
                                dry_run=dry_run,
                                custom_title=f"Example model with attack scenario I, P(r)= {prob_prebunk} and P(v)= {prob_immune}",
                                file_name='./figures/atk_1'
                            )
                            end_result_s.append(end_result.get('n_s'))
                            end_result_i.append(end_result.get('n_i'))
                            end_result_r.append(end_result.get('n_r'))

                            shares_result_s.append(shares_result.get('s'))
                            shares_result_i.append(shares_result.get('i'))
                            shares_result_r.append(shares_result.get('r'))

                            status_result_s.append(status_result.get('s'))
                            status_result_i.append(status_result.get('i'))
                            status_result_r.append(status_result.get('r'))
                            status_result_ar.append(status_result.get('ar'))
                            status_result_ui.append(status_result.get('ui'))

                        # Store the results

                        if not dry_run:
                            end_result = pd.DataFrame(dict(
                                attack_start= attack_start,
                                attack_kind=attack_kind,
                                prob_prebunk=prob_prebunk,
                                prob_immune=prob_immune,
                                prob_share_indifferent=prob_share_indifferent,
                                prob_share_disinfo=prob_share_disinfo,
                                prob_share_facts=prob_share_facts,
                                s=np.mean(end_result_s, axis=0),
                                i=np.mean(end_result_i, axis=0),
                                r=np.mean(end_result_r, axis=0)
                            ), index=[0])

                            shares_result = pd.DataFrame(dict(
                                attack_start = attack_start,
                                attack_kind = attack_kind,
                                prebunk_prob = prob_prebunk,
                                prob_immune = prob_immune,
                                prob_share_indifferent=prob_share_indifferent,
                                prob_share_disinfo=prob_share_disinfo,
                                prob_share_facts=prob_share_facts,
                                s=np.mean(shares_result_s, axis=0),
                                i=np.mean(shares_result_i, axis=0),
                                r=np.mean(shares_result_r, axis=0)
                            ))

                            status_result = pd.DataFrame(dict(
                                attack_start=attack_start,
                                attack_kind=attack_kind,
                                prebunk_prob=prob_prebunk,
                                prob_immune=prob_immune,
                                prob_share_indifferent=prob_share_indifferent,
                                prob_share_disinfo=prob_share_disinfo,
                                prob_share_facts=prob_share_facts,
                                s=np.mean(status_result_s, axis=0),
                                i=np.mean(status_result_i, axis=0),
                                r=np.mean(status_result_r, axis=0),
                                ar=np.mean(status_result_ar, axis=0),
                                ui=np.mean(status_result_ui, axis=0),
                            ))

                            store_end_result = pd.concat([store_end_result, end_result])
                            store_shares_result = pd.concat([store_shares_result, shares_result])
                            store_status_result = pd.concat([store_status_result, status_result])

                        if not store_end_result.empty:
                            store_end_result.to_csv(
                                f"end_result_atk{formatted_attack_kind}_pre{formatted_prob_prebunk}_imu{formatted_prob_immune}.csv",
                                index=False)  # Saves file without the index column
                        if not store_shares_result.empty:
                            store_shares_result.to_csv(
                                f"shares_result_atk{formatted_attack_kind}_pre{formatted_prob_prebunk}_imu{formatted_prob_immune}.csv",
                                index=False)  # Saves file without the index column

                        if not store_status_result.empty:
                            store_status_result.to_csv(
                                f"status_result_atk{formatted_attack_kind}_pre{formatted_prob_prebunk}_imu{formatted_prob_immune}.csv",
                                index=False)  # Saves file without the index column

    print('Saving complete for attack kind:', attack_kind,'.')

    print("Done.")
