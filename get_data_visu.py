#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from MulticoreTSNE import MulticoreTSNE as TSNE_multi
import pandas as pd 
import numpy as np
import json
import sys
import os
import pickle
import argparse



def scale_coords(coords, width=800, height=800):
    minx = min(coords[:,0])
    miny = min(coords[:,1])
    maxx = max(coords[:,0])
    maxy = max(coords[:,1])

    scale_x = width / (maxx - minx)
    scale_y = height / (maxy - miny)
    print(scale_x, scale_y, minx, miny, maxx, maxy)
    scaled = []
    for i in range(coords.shape[0]):
        x = coords[i,0]
        y = coords[i,1]
        scaled.append([(x - minx) * scale_x, (y - miny) * scale_y])
    return scaled


def process_features(df, pca_components, perplexity, n_jobs,output_file, tsne_alg):
    pca = PCA(n_components=pca_components, whiten=True)

    if tsne_alg=='sklearn':
        tsne = TSNE(n_components=2, perplexity=perplexity)
    else:
        tsne = TSNE_multi(n_components=2, perplexity=perplexity, n_jobs=n_jobs)
    df = df[df['features'].apply(len) == 4096]

    data = np.array(list(df['features']))
#    images = list(df['images'])

    data = pca.fit_transform(data)
    data_tsne = tsne.fit_transform(data)
    scaled_data = scale_coords(data_tsne, width=800, height=800)

    # data_json = []
    # for idx, row in df.iterrows():
    #     print(idx)
    #     x = scaled_data[idx][0]
    #     y = scaled_data[idx][1]
    #     data_json.append([x, y, row['local_thumb'], row['local_image']])

    scaled_data_array = np.array(scaled_data)
    df_json = pd.DataFrame({'a': scaled_data_array[:,0], 'b': scaled_data_array[:,1],
                            'c' : df['local_thumb'], 'd': df['local_image']})
    # str_json = 'datasets/xpca.json'
    json.dump(df_json.values.tolist(), open(output_file,'w'))

def filter_df(df,n_sample):
    df_min = df[~df.local_image.str.contains('_ver[2-9]')]
    df_min = df_min[~df_min.local_image.str.contains('_ver[0-9][0-9]')]
    df_min = df_min.sample(n_sample)
    return df_min

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help="input file generated by get_features_from_cnn.py", default="./cnn_posters_features.p")
    parser.add_argument('-o', '--output_file', help="output json file used by d3js", default='./datasets/x.json')
    parser.add_argument('-n', '--pca_components', help="number of PCA components for data reduction", default=1000, type=int)
    parser.add_argument('-p', '--perplexity', help="perplexity for TSNE", default=30, type=int)
    parser.add_argument('-j', '--n_jobs', help="number of cores to use for the tsne", type=int, default=4)
    parser.add_argument('-t', '--tsne', help='implementation tsne (multicore/sklearn', default='sklearn')
    parser.add_argument('-s', '--n_sample', help='number of sample', type=int, default=4000)
    args = parser.parse_args()

    df = pickle.load(open(args.input_file,'rb'))

    df = filter_df(df, args.n_sample)
    process_features(df, args.pca_components, args.perplexity,  args.n_jobs, args.output_file, args.tsne)



if __name__ == "__main__":
   main(sys.argv[1:])
