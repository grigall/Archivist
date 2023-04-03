import os
#import numpy as np
import pandas as pd
from datetime import date, datetime

#Pandas options
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)

def this_year():
    THIS_YEAR = date.today().year #Global date variable
    return THIS_YEAR

def today():
    TODAY = (date.today().year, date.today().month, date.today().day)
    return TODAY

def load_genres(*args, **kwargs):
    if kwargs['PATH']:
        genreList = pd.read_csv(kwargs['PATH'], sep='\t')
        genreList.sort_values(by='Genre', ascending=True, inplace=True)
        genreList.reset_index(inplace=True, drop=True)
        return genreList
    else:
        print('Genre list file error.') #DEBUG
        pass

def load_formats(*args, **kwargs):
    if kwargs['PATH']:
        formatList = pd.read_csv(kwargs['PATH'], sep='\t')
        formatList.sort_values(by='Format', ascending=True, inplace=True)
        formatList.reset_index(inplace=True, drop=True)
        return formatList
    else:
        print('Format list file error.') #DEBUG
        pass

#Math for YTD Stats
ord_today = date.toordinal(date.today())
ord_janfirst = date.toordinal(datetime.strptime(str(this_year())+'-01-01', '%Y-%m-%d'))
ytd_days = (ord_today - ord_janfirst)
ytd_weeks = ytd_days//7
ytd_months = int(ytd_days/(365/12))

def open_csv(FILE_PATH):
    #NEW_PATH = os.path.join(os.getcwd(), 'Book_Report.csv')
    data = pd.read_csv(FILE_PATH, sep='\t', encoding='utf-8')
    return data

###----- Global Functions -----###
def add_new_book(target_data, new_book_list):
    assert len(target_data.columns.tolist()) == len(new_book_list) #As of 20230210, this should be equal to 9
    df_newbook = pd.DataFrame(pd.Series(new_book_list))
    dfb = df_newbook.transpose()
    dfb.columns = target_data.iloc[:, :len(new_book_list)].columns.tolist()
    df_out = pd.concat([target_data.iloc[:, :len(new_book_list)], dfb], axis=0)
    df_out.reset_index(inplace=True, drop=True)
    return df_out

def split_by_year(dataframe):
    list_of_dfs = []
    list_of_years = list(set(dataframe.Year_Read))
    for year in list_of_years:
        year_split = dataframe.query('Year_Read == @year')
        year_split.reset_index(inplace=True, drop=True)
        list_of_dfs.append(year_split)
        
    return list_of_dfs

def get_top_three(list_of_dfs, key_col, count_col): #Pulls stats for categorical columns
    df_blank = pd.DataFrame(None)
    for df in list_of_dfs:
        #Ensure list is dynamically generated
        if len(df) < 3:
            max_range = len(df)
        else:
            max_range = 3
        assert 'Year_Read' in df.columns.tolist() #Ensure dataframe has the Year_Read column
        df_year = list(set(df.Year_Read))[0] #Pull year from Year_Read column
        top_three_output = [str(df.loc[i, key_col])+ ' ('+ str(df.loc[i, count_col]) + ')' for i in range(max_range)]
        t3_output = ', '.join([i for i in top_three_output])
        t3_out_2 = pd.Series([df_year, t3_output])
        df_out = pd.DataFrame(t3_out_2)
        df_trans = df_out.transpose()
        df_blank = pd.concat([df_blank, df_trans], axis=0)
    
    df_blank.columns = ['Year_Read', key_col]
    df_blank.reset_index(inplace=True, drop=True)
    
    return df_blank

def get_top_three_nums(list_of_dfs, sort_col): #Pulls stats for numerical columns
    df_blank = pd.DataFrame(None)
    for df in list_of_dfs:
        #Ensure list is dynamically generated
        assert 'Year_Read' in df.columns.tolist() #Ensure dataframe has the Year_Read column
        df_year = list(set(df.Year_Read))[0] #Pull year from Year_Read column
        
        description = pd.DataFrame(df.loc[:, sort_col].describe())
        d_tx = description.transpose()
        d_tx.index = [df_year]
        d_tx.reset_index(inplace=True, drop=False)

        d_tx.columns = ['Year_Read', 'Count', 'Average', 'Standard_Dev', 'Min', '25', '50', '75', 'Max']
        df_out = d_tx.loc[:, ['Year_Read', 'Count', 'Average', 'Standard_Dev', 'Min', 'Max']]
        totals_ = df.loc[:, ['Year_Read', sort_col]].groupby('Year_Read').sum()
        totals_.columns = ['Total_'+sort_col]
        totals_.reset_index(inplace=True, drop=True)
        df_out = pd.concat([df_out, totals_], axis=1)
        
        df_blank = pd.concat([df_blank, df_out], axis=0)
        df_blank.Count = df_blank.Count.astype(int)
        df_blank.Min = df_blank.Min.astype(int)
        df_blank.Max = df_blank.Max.astype(int)
    
    df_blank.columns = ['Year_Read', 'Count', 'Average_'+sort_col, 'Standard_Dev_'+sort_col, 'Min_'+sort_col, 'Max_'+sort_col, 'Total_'+sort_col]
    df_blank.reset_index(inplace=True, drop=True)

    return df_blank

def agg_and_sort(dataframe, sort_col, count_col):
    first_grp = dataframe.loc[:, ['Year_Read', sort_col, count_col]].groupby(['Year_Read',sort_col]).count()
    second_grp = first_grp.sort_values(by=['Year_Read',count_col], ascending=False)
    second_grp.reset_index(inplace=True, drop=False)
    
    return second_grp

def top_3_pipeline(dataframe, sort_col, agg_col):
    return get_top_three(split_by_year(agg_and_sort(dataframe, sort_col, agg_col)), sort_col, agg_col)

def get_page_stats(df_list, **kwargs):
    default_values = {'ytd_days': 365, 'ytd_weeks': 52, 'ytd_months': 12}
    
    if 'yoy' in kwargs:
        if kwargs['yoy'] == True:
            yoy_values = {'ytd_days': ytd_days, 'ytd_weeks': ytd_weeks, 'ytd_months': ytd_months}
        else:
            pass
    else:
        pass
    
    df_blank = pd.DataFrame(None, columns = ['Year_Read', 'Pages_per_Day', 'Pages_per_Week', 'Pages_per_Month'])

    for df in df_list:
        total_pages_read = df.Total_Length[0]
        book_year = df.Year_Read[0]
        if book_year == this_year():
            ppd = total_pages_read//yoy_values['ytd_days']
            ppw = total_pages_read//yoy_values['ytd_weeks']
            ppm = total_pages_read//yoy_values['ytd_months']
        else:
            ppd = total_pages_read//default_values['ytd_days']
            ppw = total_pages_read//default_values['ytd_weeks']
            ppm = total_pages_read//default_values['ytd_months']
        all_info = pd.DataFrame([book_year, ppd, ppw, ppm])
        ai_tx = all_info.transpose()
        ai_tx.columns = ['Year_Read', 'Pages_per_Day', 'Pages_per_Week', 'Pages_per_Month']
        df_blank = pd.concat([df_blank, ai_tx], axis=0)

    df_blank.reset_index(inplace=True, drop=True)
    return df_blank

def get_book_stats(dataframe, **kwargs):
    default_values = {'ytd_days': 365, 'ytd_weeks': 52, 'ytd_months': 12}
    
    if 'yoy' in kwargs:
        if kwargs['yoy'] == True:
            yoy_values = {'ytd_days': ytd_days, 'ytd_weeks': ytd_weeks, 'ytd_months': ytd_months}
        else:
            pass
    else:
        pass
    
    df_blank = pd.DataFrame(None, columns = ['Year_Read', 'Books_per_Day', 'Books_per_Week', 'Books_per_Month'])
    df_temp = dataframe.loc[:, ['Year_Read','Books_Read']]
    df_temp.reset_index(inplace=True, drop=False)
    df_list = split_by_year(df_temp)
    
    for df in df_list:
        book_year = df.Year_Read[0]
        if book_year == this_year():
            bpd = df.Books_Read[0]/yoy_values['ytd_days']
            bpw = df.Books_Read[0]/yoy_values['ytd_weeks']
            bpm = df.Books_Read[0]/yoy_values['ytd_months']
        else:
            bpd = df.Books_Read[0]/default_values['ytd_days']
            bpw = df.Books_Read[0]/default_values['ytd_weeks']
            bpm = df.Books_Read[0]/default_values['ytd_months']

        all_info = pd.DataFrame([book_year, bpd, bpw, bpm])
        ai_tx = all_info.transpose()
        ai_tx.columns = ['Year_Read', 'Books_per_Day', 'Books_per_Week', 'Books_per_Month']
        df_blank = pd.concat([df_blank, ai_tx], axis=0)

    df_blank.reset_index(inplace=True, drop=True)
    df_blank.Year_Read = df_blank.Year_Read.astype(int)
    return df_blank

def get_totals(df_list):
    df_blank = None
    for df in df_list:
        book_year = df.Year_Read[0]
        books_read = df.Title.count()
        auths_read = pd.Series(list(set(df.Author))).count()
        genres_read = pd.Series(list(set(df.Genre) | set(df.Genre_2))).count() #Pulls unique values from each column
        fmts_read = pd.Series(list(set(df.Format))).count()
        all_stats = pd.DataFrame([book_year, books_read, auths_read, genres_read, fmts_read])
        ai_tx = all_stats.transpose()
        ai_tx.columns = ['Year_Read', 'Books_Read', 'Authors_Read', 'Genres_Read', 'Formats_Read']
        df_blank = pd.concat([df_blank, ai_tx], axis=0)
        
    df_blank.reset_index(inplace=True, drop=True)
    return df_blank

def eoy_stats(dataframe, THIS_YEAR):
    ###----- Workflow -----###
    #Add dynamic book age column
    dataframe['Book_Age'] = [int(THIS_YEAR) - int(i) for i in dataframe.Pub_Date]

    #Split all data by year
    df_split = split_by_year(dataframe)

    ###----- Find Top Genres by Year -----###
    #Consolidate primary and secondary genres
    g1 = dataframe.loc[:, ['Year_Read', 'Genre_2', 'Genre']].groupby(['Year_Read','Genre']).count()
    g2 = dataframe.loc[:, ['Year_Read', 'Genre_2', 'Genre']].groupby(['Year_Read','Genre_2']).count()
    g1.reset_index(inplace=True, drop=False)
    g2.reset_index(inplace=True, drop=False)
    #Standardize columns
    g1.columns = ['Year_Read', 'Genre', 'Count']
    g2.columns = g1.columns.tolist()
    #Concatenate dataframes together
    genre_grp = pd.concat([g1, g2], axis=0)
    #Group by Genre and sum
    genre_grp_2 = genre_grp.groupby(['Year_Read','Genre']).sum()
    #Sort by most popular
    genre_grp_3 = genre_grp_2.sort_values(by=['Year_Read','Count'], ascending=False)
    genre_grp_3.reset_index(inplace=True, drop=False)
    my_genres = split_by_year(genre_grp_3)

    ###----- Generate All Stats -----###
    top_genres = get_top_three(my_genres, 'Genre', 'Count')
    top_genres.columns = ['Year_Read','Top_Genres']
    top_auths = top_3_pipeline(dataframe, 'Author', 'Title')
    top_auths.columns = ['Year_Read','Top_Authors']
    top_formats = top_3_pipeline(dataframe, 'Format', 'Title')
    top_formats.columns = ['Year_Read','Top_Formats']
    top_years = top_3_pipeline(dataframe, 'Pub_Date', 'Title')
    stats_book_age = get_top_three_nums(df_split, 'Book_Age')
    stats_book_age2 = stats_book_age.loc[:, ['Year_Read','Average_Book_Age', 'Standard_Dev_Book_Age', 'Min_Book_Age', 'Max_Book_Age', 'Total_Book_Age']]
    stats_length = get_top_three_nums(df_split, 'Length')
    stats_length2 = stats_length.loc[:, ['Year_Read','Average_Length', 'Standard_Dev_Length', 'Min_Length', 'Max_Length', 'Total_Length']]
    stats_page = get_page_stats(split_by_year(stats_length), yoy=True)
    book_totals = get_totals(df_split)
    book_stats = get_book_stats(book_totals, yoy=True)

    #Consolidate all dataframes in one list
    all_stats = [book_totals, top_genres, top_auths, top_formats, top_years, stats_book_age2, stats_length2, stats_page, book_stats]
    for df in all_stats:
        df.set_index('Year_Read', inplace=True, drop=True)

    #Consolidate all stats in one dataframe
    df_stats = pd.DataFrame(None)
    for stat in all_stats:
        df_stats = pd.concat([df_stats, stat], axis=1)

    return df_stats

def get_yoy_stats(dataframe):
    df_blank = pd.DataFrame(None)
    num_columns = ['Books_Read', 'Authors_Read', 'Genres_Read', 'Formats_Read', 'Average_Book_Age', 'Min_Book_Age', 'Max_Book_Age', 'Total_Book_Age', 'Average_Length', 'Min_Length', 'Max_Length', 'Total_Length', 'Pages_per_Day', 'Pages_per_Week', 'Pages_per_Month', 'Books_per_Day', 'Books_per_Week', 'Books_per_Month']
    
    if len(dataframe) > 1:
        data_copy = dataframe.loc[:, num_columns]
        for idx in range(0,len(data_copy)-1):
            #Alias both years for numerical operations
            prior_year = data_copy.iloc[idx, :]
            current_year = data_copy.iloc[idx+1, :]
            row_name = str(prior_year.name)+'-'+str(current_year.name)        

            #Aggregate, subtract, and divide for YOY Difference and YOY Percentage of Change
            yoy_diff = current_year - prior_year
            yoy_pct_chg = yoy_diff/prior_year

            #Prepare YOY Percentage of Change Stats
            df_pct = pd.DataFrame(yoy_pct_chg) 
            df_pct = df_pct.transpose()
            df_pct.columns = ['Pct_'+ col for col in df_pct.columns.tolist()] #Assign new column names for aggregation
            df_pct.index = [row_name]

            df_diff = pd.DataFrame(yoy_diff)
            df_diff = df_diff.transpose()
            df_diff.index = [row_name]

            df_combo = pd.concat([df_diff, df_pct], axis=1)

            df_blank = pd.concat([df_blank, df_combo], axis=0)

    else:
        pass
    
    return df_blank

def rpt_eoy(eoy_stats):
    eoy_list = []
    for idx in eoy_stats.index:
        report_year_txt = f'''
        Year: {idx}

        Total Books Read: {eoy_stats.Books_Read[idx]}
        Total Authors Read: {eoy_stats.Authors_Read[idx]}
        Total Genres Read: {eoy_stats.Genres_Read[idx]}
        Total Formats Read: {eoy_stats.Formats_Read[idx]}
        Total Pages Read: {eoy_stats.Total_Length[idx]}

        Most Read Genre(s): {eoy_stats.Top_Genres[idx]}
        Most Read Author(s): {eoy_stats.Top_Authors[idx]}
        Most Read Format(s): {eoy_stats.Top_Formats[idx]}
        Most Popular Year(s): {eoy_stats.Pub_Date[idx]} 

        Average Age: {round(eoy_stats.Average_Book_Age[idx],1)} year(s) old (Standard Deviation: +/-{round(eoy_stats.Standard_Dev_Book_Age[idx],1)} year(s))
        Newest Book: {eoy_stats.Min_Book_Age[idx]} year(s) old
        Oldest Book: {eoy_stats.Max_Book_Age[idx]} year(s) old

        Average Pages per Book: {round(eoy_stats.Average_Length[idx],1)} pages
        Shortest Book: {eoy_stats.Min_Length[idx]} pages
        Longest Book: {eoy_stats.Max_Length[idx]} pages

        Average Pages-per-Day: {round(eoy_stats.Pages_per_Day[idx],1)}
        Average Pages-per-Week: {round(eoy_stats.Pages_per_Week[idx],1)}
        Average Pages-per-Month: {round(eoy_stats.Pages_per_Month[idx],1)}

        Average Books-per-Day: {round(eoy_stats.Books_per_Day[idx],2)}
        Average Books-per-Week: {round(eoy_stats.Books_per_Week[idx],2)}
        Average Books-per-Month: {round(eoy_stats.Books_per_Month[idx],2)}    
        '''
        eoy_list.append(report_year_txt)
        
    return eoy_list

def rpt_yoy(yoy_stats):
    yoy_list = []
    for idx in yoy_stats.index:
        report_year_txt = f'''
        Year-over-Year: {idx}

        TOTAL CHANGE (% CHANGE)
        
        Total Books Read: {yoy_stats.Books_Read[idx]} ({round(yoy_stats.Pct_Books_Read[idx]*100,2)}%)
        Total Authors Read: {yoy_stats.Authors_Read[idx]} ({round(yoy_stats.Pct_Authors_Read[idx]*100,2)}%)
        Total Genres Read: {yoy_stats.Genres_Read[idx]} ({round(yoy_stats.Pct_Genres_Read[idx]*100,2)}%)
        Total Formats Read: {yoy_stats.Formats_Read[idx]} ({round(yoy_stats.Pct_Formats_Read[idx]*100,2)}%)
        Total Pages Read: {yoy_stats.Total_Length[idx]} ({round(yoy_stats.Pct_Total_Length[idx]*100,2)}%)

        Average Age (years): {round(yoy_stats.Average_Book_Age[idx],1)} ({round(yoy_stats.Pct_Average_Book_Age[idx]*100,2)}%)
        Newest Book (years): {yoy_stats.Min_Book_Age[idx]} ({round(yoy_stats.Pct_Min_Book_Age[idx]*100,2)}%)
        Oldest Book (years): {yoy_stats.Max_Book_Age[idx]} ({round(yoy_stats.Pct_Max_Book_Age[idx]*100,2)}%)

        Average Pages per Book: {round(yoy_stats.Average_Length[idx],1)} ({round(yoy_stats.Pct_Average_Length[idx]*100,2)}%)
        Shortest Book (pages): {yoy_stats.Min_Length[idx]} ({round(yoy_stats.Pct_Min_Length[idx]*100,2)}%)
        Longest Book (pages): {yoy_stats.Max_Length[idx]} ({round(yoy_stats.Pct_Max_Length[idx]*100,2)}%)

        Average Pages-per-Day: {round(yoy_stats.Pages_per_Day[idx],1)} ({round(yoy_stats.Pct_Pages_per_Day[idx]*100,2)}%)
        Average Pages-per-Week: {round(yoy_stats.Pages_per_Week[idx],1)} ({round(yoy_stats.Pct_Pages_per_Week[idx]*100,2)}%)
        Average Pages-per-Month: {round(yoy_stats.Pages_per_Month[idx],1)} ({round(yoy_stats.Pct_Pages_per_Month[idx]*100,2)}%)

        Average Books-per-Day: {round(yoy_stats.Books_per_Day[idx],2)} ({round(yoy_stats.Pct_Books_per_Day[idx]*100,2)}%)
        Average Books-per-Week: {round(yoy_stats.Books_per_Week[idx],2)} ({round(yoy_stats.Pct_Books_per_Week[idx]*100,2)}%)
        Average Books-per-Month: {round(yoy_stats.Books_per_Month[idx],2)} ({round(yoy_stats.Pct_Books_per_Month[idx]*100,2)}%)    
        '''
        yoy_list.append(report_year_txt)
        
    return yoy_list


