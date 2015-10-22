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
float find_max_len_consec_sequence_1d(const float *indata,int i, int j, float thresh, float fill_val, char *operation, int *index_event_start, int *index_event_end);
void find_max_len_consec_sequence_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, char *operation, int *tab_index_event_start, int *tab_index_event_end);
float find_GSL_1d(const float *indata,int i, int j, float thresh, float fill_val, int indexMiddleOfYear);
void find_GSL_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, int indexMiddleOfYear);
double getElementAt_2(const float *table, int t, int i, int j);
float WSDI_CSDI_1d(const float *indata,int i, int j, int N);
void WSDI_CSDI_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, int N);
void percentile_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int percentile, float fill_value,  char * interpolation);
double percentile_1d(const float *indata, int i, int j, char * interpolation);
float* get_tab_1d(const float *indata, int i, int j, int* new_size);
double get_percentile(float* tab_1d, int len_tab_1d);
double get_percentile2(float* tab_1d, int len_tab_1d);
void swap(float* a, float* b);
void qs(float* s_arr, int first, int last);
double get_run_stat_1d(const float *indata, int i, int j, int w_width, float fill_val, char * stat_mode, char * extreme_mode, int *index_event);
void get_run_stat_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int w_width, float fill_val, char * stat_mode, char * extreme_mode, int *index_event);
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


//Segmentation fault (core dumped)
//http://stackoverflow.com/questions/13654449/error-segmentation-fault-core-dumped

float find_max_len_consec_sequence_1d(const float *indata,int i, int j, float thresh, float fill_val, char *operation, int *index_event_start, int *index_event_end)
{
// find max length of a consecutive sequence in 1D array in a chosen logical condition ("gt", "get", "lt", "let", "e")
    float previous=-999;
    float nb_max=0;
    int nb=0;
    int t;
    int all_fillval = 1;

    *index_event_start=-1;
    *index_event_end=-1;
    int index=-1;

    ///////////   >
    if (strcmp(operation,"gt")==0)
    {

        for (t = 0; t < sizeT; t++)
        {
            //double val = getElementAt(indata,t,i,j);
            float val = getElementAt(indata,t,i,j);

            if ((val>thresh) && (val != fill_val))
            {
              if ((previous>thresh) && (previous != fill_val))
            	  nb++;
              else
              {
            	  nb=1;
            	  index=t;
              }
            }
            else
            	nb=0;
            
            if (val != fill_val) all_fillval = 0;

            // If several sequences have the same length nb_max,
            // if (nb>nb_max): then the 1st sequence is taken into account for index_event_start
            // if (nb>=nb_max): then the last sequence is taken into account for index_event_start
            if (nb>nb_max)
			{
            	nb_max=(float)nb;
            	*index_event_start=index;
            	*index_event_end = index+nb_max-1;
			}
            
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
              if ((previous>=thresh) && (previous != fill_val))
            	  nb++;
              else
              {
            	  nb=1;
            	  index=t;
              }
            }
            else
            	nb=0;

            if (val != fill_val) all_fillval = 0;

            // If several sequences have the same length nb_max,
            // if (nb>nb_max): then the 1st sequence is taken into account for index_event_start
            // if (nb>=nb_max): then the last sequence is taken into account for index_event_start
            if (nb>nb_max)
			{
            	nb_max=(float)nb;
            	*index_event_start=index;
            	*index_event_end = index+nb_max-1;
			}
            
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
              if ((previous<thresh) && (previous != fill_val))
            	  nb++;
              else
              {
            	  nb=1;
            	  index=t;
              }
            }
            else
            	nb=0;

            if (val != fill_val) all_fillval = 0;

            // If several sequences have the same length nb_max,
            // if (nb>nb_max): then the 1st sequence is taken into account for index_event_start
            // if (nb>=nb_max): then the last sequence is taken into account for index_event_start
            if (nb>nb_max)
			{
            	nb_max=(float)nb;
            	*index_event_start=index;
            	*index_event_end = index+nb_max-1;
			}
            
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
              if ((previous<=thresh) && (previous != fill_val))
            	  nb++;
              else
              {
            	  nb=1;
            	  index=t;
              }
            }
            else
            	nb=0;

            if (val != fill_val) all_fillval = 0;

            // If several sequences have the same length nb_max,
            // if (nb>nb_max): then the 1st sequence is taken into account for index_event_start
            // if (nb>=nb_max): then the last sequence is taken into account for index_event_start
            if (nb>nb_max)
			{
            	nb_max=(float)nb;
            	*index_event_start=index;
            	*index_event_end = index+nb_max-1;
			}
            
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
              if ((previous==thresh) && (previous != fill_val))
            	  nb++;
              else
              {
            	  nb=1;
            	  index=t;
              }
            }
            else
            	nb=0;

            if (val != fill_val) all_fillval = 0;

            // If several sequences have the same length nb_max,
            // if (nb>nb_max): then the 1st sequence is taken into account for index_event_start
            // if (nb>=nb_max): then the last sequence is taken into account for index_event_start
            if (nb>nb_max)
			{
            	nb_max=(float)nb;
            	*index_event_start=index;
            	*index_event_end = index+nb_max-1;
			}
            
            previous=val;
        }
    }

    if (all_fillval == 1) nb_max = fill_val;

    return nb_max;
}


// function called from Python
void find_max_len_consec_sequence_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float thresh, float fill_val, char *operation, int *tab_index_event_start, int *tab_index_event_end)
{
// find max length of a consecutive sequence in 3D array (along time axis) in a logical condition

    //outdata = (double *) malloc (_sizeI*_sizeJ*sizeof(double));
    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;
    int index_event_start=-1;
    int index_event_end=-1;

        for (i = 0; i < sizeI; i++)
        {
            for (j = 0; j < sizeJ; j++)
            {
                //outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,temp);
                outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,thresh, fill_val, operation, &index_event_start, &index_event_end);
                tab_index_event_start[i*sizeJ+j] = index_event_start;
                tab_index_event_end[i*sizeJ+j] = index_event_end;
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


// function called from Python
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
// percentiles computation: begin
//////////////////////////////////////////////////////////////////////////////////// 



// function called from Python 
void percentile_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int percentile, float fill_value, char * interpolation)
{

    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;

    for (i = 0; i < sizeI; i++)
    {

        for (j = 0; j < sizeJ; j++)
        {
            outdata[i*sizeJ+j] = percentile_1d(indata, i, j, interpolation);
        }
    }

}







// for 1D array 
double percentile_1d(const float *indata, int i, int j, char * interpolation)
{
    int new_size = 0;
    
    float* new_tab =  get_tab_1d(indata, i,j,&new_size);
    
    qs(new_tab, 0, sizeT-1);
    
    // begin print
//    int xx;
//    for(xx=0; xx<sizeT; xx++)
//    {
//    	printf("%f", new_tab[xx]);
//    	printf("\n");
//    }
//    printf("+++++");

//    printf("%f", new_tab[new_size-1]);
//    printf("\n");
//    printf("%f", new_tab[new_size]);
//    printf("\n");
//    printf("+++++");
//    printf("\n");

    //printf("%d", new_size);
    //printf("\n");

    // end print

    double perc;

    if (strcmp(interpolation,"linear")==0)
    {
    	perc =  get_percentile(new_tab, new_size);
    }
    else if (strcmp(interpolation,"hyndman_fan")==0)
    {
    	perc =  get_percentile2(new_tab, new_size);
    }

      
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



double get_percentile2(float* tab_1d, int len_tab_1d)

	// interpolation of Hyndman and Fan (https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf)

//	percentile<-function(n,x,pctile){
//
//			 x1<-x[is.na(x)==F]
//
//			 n1<-length(x1)
//
//			 a<-mysort(x1,decreasing=F)
//
//			 b<-n1*pctile+0.3333*pctile+0.3333
//
//			 bb<-trunc(b)
//
//			 percentile<-a[bb]+(b-bb)*(a[bb+1]-a[bb]) }#end
//
//
//	 # pseudo code
//
//	 func percentile(n, x, perc_val):
//
//		x1 = x where missin_values = False
//		n1 = len(x1)
//		a = sort(n1)
//		b = n1 * perc_val + 0.3333 * perc_val + 0.3333
//		bb = round(b) # !!! round to down, i.e. 2.9 ---> 2
//		percentile = a[bb] + (b-bb)*(a[bb+1]-a[bb])


{
    if (len_tab_1d==0) return fill_value;
    if (len_tab_1d==1) return tab_1d[0];


    double p = percentile * 0.01;


    //double index = (len_tab_1d-1) * p + (1+p)/3. ;
    double index = (len_tab_1d) * p + (1+p)/3. ;

    double index_integer_part;

    modf(index, &index_integer_part);
    int i = index_integer_part;

    double perc = tab_1d[i-1] + (index-i)*(tab_1d[i]-tab_1d[i-1]);

    return perc;
}

double get_percentile(float* tab_1d, int len_tab_1d)

	// linear interpolation

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

/////////////////////////////////////////////////////////////////////////////////////
// percentiles computation: end
////////////////////////////////////////////////////////////////////////////////////


void get_run_stat_3d(const float *indata, int _sizeT, int _sizeI, int _sizeJ, double *outdata, int w_width, float fill_val, char * stat_mode, char * extreme_mode, int *tab_index_event)
{
// find max sum of a consecutif sequence of w_width elements (sliding window of size=w_width) (along time axis)

    setGlobalVariables(_sizeT,_sizeI,_sizeJ, fill_value, percentile);
    int i,j;
    int index_event=-1;

        for (i = 0; i < sizeI; i++)
        {
            for (j = 0; j < sizeJ; j++)
            {
                outdata[i*sizeJ+j] = get_run_stat_1d(indata, i, j, w_width, fill_val, stat_mode, extreme_mode, &index_event);
                tab_index_event[i*sizeJ+j] = index_event;
            }
        }
}


double get_run_stat_1d(const float *indata, int i, int j, int w_width, float fill_val, char * stat_mode, char * extreme_mode, int *index_event)
{
	int t, tt;
	*index_event = -1; // initialize the index_event to -1 (i.e. no correct value is found yet)

	// extreme_oper is 'min' or 'max'
	int extreme_mode_max=(strcmp(extreme_mode,"max")==0);
	int extreme_mode_min=(strcmp(extreme_mode,"min")==0);

	// stat_mode is 'sum' or 'mean'
	int stat_mode_sum = (strcmp(stat_mode,"sum")==0);
	int stat_mode_mean = (strcmp(stat_mode,"mean")==0);

	float extreme_val, val;
	if (extreme_mode_max) extreme_val=-1.0;
	else if (extreme_mode_min) extreme_val=9999999999;


	for (t=0; t<=sizeT-w_width; t++)

	{
		// all_values_ok (boolean) =>  no fill_value found in window (w_width)
		int all_values_ok=1;

		float sum = 0.0;


    	for (tt=t; tt<t+w_width; tt++)
    	{
    		val = getElementAt(indata,tt,i,j);
    		all_values_ok = all_values_ok && val!=9999;
    		if (!all_values_ok) break; // if a fill_value is found, then no need to finish calculation the sum in the window
    		sum += val;
    	}


    	if ((extreme_mode_max && all_values_ok && sum>extreme_val) || (extreme_mode_min && all_values_ok && sum<extreme_val))
    	{
    		extreme_val = sum;
    		*index_event = t;// memorize the 1st index of the window where extreme val is found (minSum or maxSum)
    	}

	}

	if (*index_event == -1)
		return (double) fill_val;

	else if (stat_mode_sum)
		return (double)  extreme_val;

	else if (stat_mode_mean)
		return (double) (extreme_val*1.0)/w_width; // if a sum is max(min), then mean is max(min) also

	else return (double) fill_val;
}




//  gcc -std=c99 libC.c
//  ./a.out
int main() 
{
    //printf('HELLO WORLD !!!')


    return 0;

}    


