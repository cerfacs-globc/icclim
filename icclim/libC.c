//  Copyright CERFACS (http://cerfacs.fr/)
//  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
//
//  Author: Natalia Tatarinova

/* To compile:

gcc -fPIC -g -c -Wall libC.c
gcc -shared -o libC.so libC.o

OR

gcc -fPIC -g -c -Wall -std=c99 libC.c
gcc -shared -o libC.so -std=c99 libC.o

*/



#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Global variables
int sizeT,sizeI,sizeJ;
float fill_value;
int percentile;

/////////////////////////////////////////////////////////////////////
// Function prototypes

void setGlobalVariables(int _sizeT,int _sizeI,int _sizeJ,float _fill_value, int _percentile);
double getElementAt(const float *table, int t, int i, int j);
float find_max_len_consec_sequence_1d(const float *indata,int i, int j, float thresh, float fill_val, char *operation);
void find_max_len_consec_sequence_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, char *operation);
float get_max_sum_window_1d(const float *indata, int i, int j, int w_width, float fill_val);
void find_max_sum_slidingwindow_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int w_width, float fill_val);
float find_GSL_1d(const float *indata,int i, int j, float thresh, float fill_val, int indexMiddleOfYear);
void find_GSL_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, int indexMiddleOfYear);
double getElementAt_2(const float *table, int t, int i, int j);
float WSDI_CSDI_1d(const float *indata,int i, int j, int N);
void WSDI_CSDI_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, int N);
void percentile_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int percentile, float fill_value);
double percentile_1d(const float *indata, int i, int j);
float* get_tab_1d(const float *indata, int i, int j, int* new_size);
double get_percentile(float* tab_1d, int len_tab_1d);
void swap(float* a, float* b);
void qs(float* s_arr, int first, int last);

/////////////////////////////////////////////////////////////////////




void setGlobalVariables(int _sizeT,int _sizeI,int _sizeJ,float _fill_value, int _percentile)
{
    sizeT = _sizeT;
    sizeI = _sizeI;
    sizeJ = _sizeJ;
    fill_value = _fill_value;
    percentile = _percentile;
}

//double getElementAt(const double *table, int t, int i, int j)
double getElementAt(const float *table, int t, int i, int j)
{
    return table[t*sizeI*sizeJ + i*sizeJ +j];
}




// ERROR
//Segmentation fault (core dumped)
//http://stackoverflow.com/questions/13654449/error-segmentation-fault-core-dumped

float find_max_len_consec_sequence_1d(const float *indata,int i, int j, float thresh, float fill_val, char *operation)
{
// find max length of a consecutive sequence in 1D array in a chosen logical condition ("gt", "get", "lt", "let", "e")
    float previous=-999;
    float nb_max=0;
    int nb=0;
    int t;
    int all_fillval = 1;

    ///////////   >
    if (strcmp(operation,"gt")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val>thresh) && (val != fill_val))
            {
              if (previous>thresh) nb++;
                else nb=1;	    
            }
            else
              nb=0;
            
            if (val != fill_val) all_fillval = 0;

            if (nb>nb_max) nb_max=(float)nb;
            
            previous=val;
        }
    }
    
    ///////////   >=    
    else if (strcmp(operation,"get")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val>=thresh) && (val != fill_val))
            {
                if (previous>=thresh) nb++;
                else nb=1;	    
            }
            else
              nb=0;

            if (val != fill_val) all_fillval = 0;

            if (nb>nb_max) nb_max=(float)nb;
            
            previous=val;
        }
    }    
    
    ///////////   <
    else if (strcmp(operation,"lt")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val<thresh) && (val != fill_val))
                {
                    if (previous<thresh) nb++;
                    else nb=1;	    
                }
            else
              nb=0;

            if (val != fill_val) all_fillval = 0;

            if (nb>nb_max) nb_max=(float)nb;
            
            previous=val;
        }
    }
    
    ///////////   <=
    else if (strcmp(operation,"let")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val<=thresh) && (val != fill_val))
            {
                if (previous<=thresh) nb++;
                else nb=1;	    
            }
            else
              nb=0;

            if (val != fill_val) all_fillval = 0;

            if (nb>nb_max) nb_max=(float)nb;
            
            previous=val;
        }
    }
    
    ///////////   =
    else if (strcmp(operation,"e")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val==thresh) && (val != fill_val))
            {
                if (previous==thresh) nb++;
                else nb=1;	    
            }
            else
              nb=0;

            if (val != fill_val) all_fillval = 0;

            if (nb>nb_max) nb_max=(float)nb;
            
            previous=val;
        }
    }

    if (all_fillval == 1) nb_max = fill_val;

    return nb_max;
}


// fonction appelee depuis python 
void find_max_len_consec_sequence_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, char *operation) 
{
// find max length of a consecutive sequence in 3D array (along time axis) in a logical condition

    //outdata = (double *) malloc (_sizeI*_sizeJ*sizeof(double));
    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;

        for (i = 0; i < sizeI; i++)
        {
            for (j = 0; j < sizeJ; j++)
            {
                //outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,temp);
                outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,temp, fill_val, operation); 
            }
        }
}
    

float get_max_sum_window_1d(const float *indata, int i, int j, int w_width, float fill_val)
{
    float max_sum=0.0;
    float sum=0.0;
    int t;
    float val, val_to_subtract;
    int all_fillval = 1;

    // initialize max_sum [for the first (w_width-1) elements]
    for (t=0; t<w_width; t++)
    {
        val = getElementAt(indata,t,i,j);
        
        if (val==fill_val)
          val=0.0;
        else
          all_fillval = 0;
        
        sum += val;
    }
    
    max_sum = sum;      
    
    // calculate the current sum, and compare it to the max_sum               
    for (t=w_width; t<=sizeT-1; t++) 
    {
        val = getElementAt(indata,t,i,j);
        if (val==fill_val)
          val=0.0;
        else
          all_fillval = 0;

        sum += val;                                 // previous sum + following element
        
        val_to_subtract = getElementAt(indata,t-w_width,i,j);
        if (val_to_subtract==fill_val) val_to_subtract=0.0;
        sum -= val_to_subtract;                      // current sum

        if (sum > max_sum) max_sum =  sum;
        
    }    

    if (all_fillval == 1) max_sum = fill_val;

    return max_sum;
}
    

void find_max_sum_slidingwindow_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int w_width, float fill_val)
{
// find max sum of a consecutif sequence of w_width elements (sliding window of size=w_width) (along time axis)

    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile); 
    int i,j;
    
        for (i = 0; i < sizeI; i++)
        {
            for (j = 0; j < sizeJ; j++)
            {
                outdata[i*sizeJ+j] = get_max_sum_window_1d(indata, i, j, w_width, fill_val); 
            }
        }
}






// indexMiddleOfYear is the index of the 1st day in the 2nd semester for which we have a value for temperature
// -> in a complete year, it should be the 1st of july : indexMiddleOfYear = 181 (or 182 in a bissextile year)
float find_GSL_1d(const float *indata,int i, int j, float thresh, float fill_val, int indexMiddleOfYear)
{
    float previous=-999;
    int nb=0;
    int t;
    int sequenceLength=6;
    int T1 = -1;
    int T2 = -1;
    float returnValue;
    
    // - search T1 : beginning of 1st sequence of at least 6 consecutive days with temp > thresh
    // - the search is done from 1st day of year to the last day of year
    for (t = 0; t < sizeT; t++)
    {
        float val = getElementAt(indata,t,i,j);

        if ((val>thresh) && (val != fill_val))
        {
            if (previous>thresh) nb++;
            else nb=1;	
        }
        else nb=0;
        
        previous=val;
        
        if (nb == sequenceLength) // found T1
        { 
            T1 = t-sequenceLength+1;
            break; // if we found at least 6 consecutive days with temp > thresh, we exit from the for loop
        }
        
    }
    
    // - search T2 : beginning of 1st sequence of at least 6 consecutive days with temp < thresh
    // - the search is done from the index indexMiddleOfYear to the last day of year.
    // - indexMiddleOfYear should usually be the index of 1st of July, i.e 181 in a normal year
    previous=999;
    nb=0;
    for (t = indexMiddleOfYear; t < sizeT; t++)
    {
        float val = getElementAt(indata,t,i,j);

        if ((val<thresh) && (val != fill_val))
        {
            if (previous<thresh) nb++;
            else nb=1;	
        }
        else nb=0;
        
        previous=val;
        
        if (nb == sequenceLength) // found T2
        { 
            T2 = t-sequenceLength+1;
            break; // if we found at least 6 consecutive days with temp < thresh, we exit from the for loop
        }
        
    }
    
    
    // calculate the return value of this function
    if (T1!=-1 && T2!=-1 && T1<T2)  // T1 and T2 were found and T1<T2 : we can calculate a result for find_GSL_1d
    { 
      returnValue = (float) (T2-T1);
    }
    else                            // impossible to return a result for find_GSL_1d, so we return fill_val
    { 
        returnValue = fill_val;
    }
    
    
    return returnValue;
    
}




void find_GSL_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, int indexMiddleOfYear)
{

    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;
    
        for (i = 0; i < sizeI; i++)
        {
            for (j = 0; j < sizeJ; j++)
            {
                outdata[i*sizeJ+j] = find_GSL_1d(indata,i,j,temp, fill_val, indexMiddleOfYear);
            }
        }
}
 


///////////////////////////// WSDI and CSDI indices (counting numbers when consecutive sequence is at least of 6)



// same as getElementAt, but returns 0 if t == sizeT
// we simulate an additionnal zero at the end of the array (ref: WSDI_CSDI_1d)
double getElementAt_2(const float *table, int t, int i, int j)
{
    if (t==sizeT) return 0;
    else return getElementAt(table,  t,  i,  j);
}


// for a 1D array, find     
float WSDI_CSDI_1d(const float *indata,int i, int j, int N)
// equivalent code in Python:
/*
sum_glob = 0
sum_portion = 0

for i in range(len(a)):
    
    a = numpy.append(a, 0)
    
    if a[i]==1:
        sum_portion += 1
        
        if sum_portion >= N and a[i+1]==0: 
            sum_glob += sum_portion
            
            
    elif a[i]==0:
        sum_portion = 0
*/

{
    float sum_portion = 0;
    float sum_glob = 0;
    float val;
    int t;
  
    for (t = 0; t < sizeT; t++)
    {
        val = getElementAt_2(indata,t,i,j);
        
        if (val == 1)
        {
            sum_portion += 1;
    
            if (sum_portion >= N && getElementAt_2(indata,t+1,i,j) == 0)  sum_glob += sum_portion;
        }
        
        else
        {
            if (val == 0) sum_portion = 0;
        }
        
    }
    
    return sum_glob;
    
}


// fonction appelee depus python 
void WSDI_CSDI_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, int N) 
{
    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;
    
    for (i = 0; i < sizeI; i++)
    {
        for (j = 0; j < sizeJ; j++)
        {
            outdata[i*sizeJ+j] = WSDI_CSDI_1d(indata,i,j,N); 
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////
// percentiles computation
//////////////////////////////////////////////////////////////////////////////////// 



// function called from Python 
void percentile_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int percentile, float fill_value) 
{

    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;

    for (i = 0; i < sizeI; i++)
    {

        for (j = 0; j < sizeJ; j++)
        {
            outdata[i*sizeJ+j] = percentile_1d(indata, i, j);
        }
    }

}



// for 1D array 
double percentile_1d(const float *indata, int i, int j)
{
    int new_size = 0;
    
    float* new_tab =  get_tab_1d(indata, i,j,&new_size);
    
    qs(new_tab, 0, sizeT-1);
    
    double perc =  get_percentile(new_tab, new_size);
      
    free(new_tab);

    return  perc;
}


// indata is actually a 3D array represented in one big 1D array
float* get_tab_1d(const float *indata, int i, int j, int* new_size)
{
    float* tab_1d;
    float val;
    int nb_fill_values = 0;
    
    // we reserve memory for tab_1d
    tab_1d = (float *) malloc (sizeT*sizeof(float));
    
    // we copy values from indata at (i,j) to tab_1d
    int t;
    for(t=0; t<sizeT; t++)
    {
        val = getElementAt(indata,t,i,j);
        tab_1d[t]=val;
        if (val == fill_value)
        {  
            nb_fill_values++;
        }
    }
    
    *new_size = sizeT-nb_fill_values;
    
    return tab_1d;
    
}



double get_percentile(float* tab_1d, int len_tab_1d)
{
    if (len_tab_1d==0) return fill_value;
    if (len_tab_1d==1) return tab_1d[0];
    
    double p = percentile * 0.01;
    double index = p * (len_tab_1d-1);
    double index_integer_part, index_fractional_part;        
    double perc;
    int  i, j;
    
    index_fractional_part = modf(index, &index_integer_part);
    

    i = index_integer_part;
    j = i + 1;
    
    perc = index_fractional_part * (tab_1d[j] - tab_1d[i]) + tab_1d[i];
    return perc;
    
}

////////////// QUICK SORT
// taken from: http://ru.wikibooks.org/wiki/%D0%A0%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8_%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D0%BE%D0%B2/%D0%A1%D0%BE%D1%80%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0/%D0%91%D1%8B%D1%81%D1%82%D1%80%D0%B0%D1%8F

void swap(float* a, float* b)
{
    float temp = *a;
    *a = *b;
    *b = temp;
}


void qs(float* s_arr, int first, int last)
{
    int i = first, j = last;
    float x = s_arr[(first + last) / 2];
 
    do {
            while (s_arr[i] < x) i++;
            while (s_arr[j] > x) j--;
     
            if(i <= j)
            {
                if (s_arr[i] > s_arr[j]) swap(&s_arr[i], &s_arr[j]);
                i++;
                j--;
            }
        } while (i <= j);
 
    if (i < last)
        qs(s_arr, i, last);
    if (first < j)
        qs(s_arr, first, j);
}





//  gcc -std=c99 libC.c
//  ./a.out
int main() 
{
    //printf('HELLO WORLD !!!')
    return 0;
}    


