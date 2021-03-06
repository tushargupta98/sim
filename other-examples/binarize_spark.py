#!/usr/bin/env python

from pyspark import SparkContext, SparkConf
import nibabel as nib
from gzip import GzipFile
from io import BytesIO
import numpy as np
import argparse
import os
from hdfs import Config

def save_nifti(x, output, client):
    filename = x[0].split('/')[-1]
    im = nib.Nifti1Image(x[1][1], x[1][0])
    nib.save(im, filename)
    client.upload(output,filename, overwrite=True)
    return (x[0], 0)

def binarize(x, threshold):
    return (x[0],(x[1][0], np.where(x[1][1] > threshold, np.iinfo(x[1][1].dtype).max, 0)))

def binarize_and_save(x, threshold, output, client):
    bin_data = np.where(x[1][1] > threshold, np.iinfo(x[1][1].dtype).max, 0)
    return save_nifti((x[0], (x[1][0], bin_data)), output, client)
    
def get_data(x):
    fh = nib.FileHolder(fileobj=GzipFile(fileobj=BytesIO(x[1])))
    im = nib.Nifti1Image.from_file_map({'header': fh, 'image': fh})
    return (x[0], (im.affine, im.get_data()))

def main():

    conf = SparkConf().setAppName("binarize nifti")
    sc = SparkContext(conf=conf)
    sc.setLogLevel('ERROR')


    parser = argparse.ArgumentParser(description='Binarize images')
    parser.add_argument('threshold', type=int, help="binarization threshold")
    parser.add_argument('folder_path', type=str, help='folder path containing all of the splits')
    parser.add_argument('output_path', type=str, help='output folder path')
    parser.add_argument('num', type=int,choices=[2,4,6,8], help='number of binarization operations')
    parser.add_argument('-m', '--in_memory', type=bool, default=True,  help='in memory computation')    

    args = parser.parse_args()
    
    nibRDD = sc.binaryFiles(args.folder_path)\
        .map(lambda x: get_data(x))

    client = Config().get_client('dev')

    if args.in_memory == 'True':
        print "Performing in-memory computations"

        for i in xrange(num - 1):
           nibRDD = nibRDD.map(lambda x: binarize(x, args.threshold))
        nibRDD = nibRDD.map(lambda x: binarize_and_save(x, args.threshold, args.output_path, client)).collect()
            
    else:
        print "Writing intermediary results to disk and loading from disk"

        binRDD = nibRDD.map(lambda x: binarize_and_save(x, args.threshold, args.output_path + "1", client)).collect()

        for i in xrange(num - 1):
           binRDD = sc.binaryFiles(args.output_path + "1")\
                        .map(lambda x: get_data(x))\
                        .map(lambda x: binarize_and_save(x, args.threshold, args.output_path + "1", client)).collect()

if __name__ == "__main__":
    main()
