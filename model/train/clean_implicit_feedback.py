#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 10:36:03 2020

@author: sebastianren
"""
import clean_data
import numpy
import csv
import json
import pandas as pd
from io import StringIO

movies = []
#Temporirly not used for M1
def clean_implicit():
    # implicit_fb = pd.read_csv('raw_data/movie_interest.csv')
    with open('movie_interest.csv', 'r') as f:
        implicit_fb = csv.DictReader(f)
        
        with open("implicit_fb.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["web_id", "user_id", "interest"])

            iter = 0
            for record in implicit_fb:
                
                if iter % 10000 == 0:
                    print(iter)
                iter += 1
                
                web_id = clean_data.find_web_id(record['movie_id'])
                if web_id != -1:
                    writer.writerow([web_id, record['user_id'], float(record['rating'])])
                else:
                    continue


if __name__ == "__main__":
    clean_data. clear_movie()
    clean_implicit()