#!/usr/bin/env python
import pandas as pd

def main():
    df = pd.read_csv('movies2016.csv', encoding='utf-8')
    # Checking unknown gender
    print df[df['gender'] == 'unknown']
    # Patch missing genders
    df.loc[df['id'] == 'nm2609807', 'gender'] = 'female'
    df.loc[df['gender'] == 'unknown', 'gender'] = 'male'
    # gender breakdown
    gender_breakdown = df.groupby(['role', 'gender']).size().reset_index(name='count')
    gender_breakdown['total'] = gender_breakdown.groupby(['role'])['count'].transform('sum')
    gender_breakdown['percentage'] = 100 * gender_breakdown['count'] / gender_breakdown['total']
    print gender_breakdown
    print df[(df['gender'] == 'female') & (df['role'] == 'director')]

if __name__ == '__main__':
    main()