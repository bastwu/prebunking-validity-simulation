from runModel import run_model



if __name__ == '__main__':

    run_model(
        pop_size=100,
        n_ticks=100,
        n_friends=5,
        n_add=5,
        prob_share=.5,

        attack_start=5,
        attack_kind=1,
        atk_len=3,
        atk_str=50,
        decay=10,
        dark_quantile=.75,

        prebunk_prob=.3,
        prob_immune=.1,
        # draw = False,
        verbose=False,
        node_mult=25,
        custom_title='Example model with attack scenario I, P(r)=.3 and P(v)=.1',
        file_name='./figures/atk_1'
    )