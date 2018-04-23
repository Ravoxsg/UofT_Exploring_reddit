## Scripts shoulc be used in this order:

1: extract_glove_data.py to build the required .csv file for community embeddings representation

2: community2vecpaper.R to get these community embeddings representation

3: generate_random_pair.py to fill in pairs for each group

4: process_pairs.py to compute average distances in each pair

5: threads.py to extract monthly commenting data for each subreddit of interest

6: community_connectivity.py to build graph data for pairs of communities

7: plotting_output.py to plot graph properties
