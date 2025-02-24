/* TA-LIB Copyright (c) 1999-2024, Mario Fortier
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 * - Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * - Neither name of author nor the names of its contributors
 *   may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/* List of contributors:
 *
 *  Initial  Name/description
 *  -------------------------------------------------------------------
 *  MF       Mario Fortier
 *  JV       Jesus Viver <324122@cienz.unizar.es>
 *
 *
 * Change history:
 *
 *  MMDDYY BY   Description
 *  -------------------------------------------------------------------
 *  112400 MF   Template creation.
 *  010503 MF   Fix to always use SMA for the STDDEV (Thanks to JV).
 *  052603 MF   Adapt code to compile with .NET Managed C++
 *
 */

/**** START GENCODE SECTION 1 - DO NOT DELETE THIS LINE ****/
/* All code within this section is automatically
 * generated by gen_code. Any modification will be lost
 * next time gen_code is run.
 */
/* Generated */ 
/* Generated */ #if defined( _MANAGED )
/* Generated */    #include "TA-Lib-Core.h"
/* Generated */    #define TA_INTERNAL_ERROR(Id) (RetCode::InternalError)
/* Generated */    namespace TicTacTec { namespace TA { namespace Library {
/* Generated */ #elif defined( _JAVA )
/* Generated */    #include "ta_defs.h"
/* Generated */    #include "ta_java_defs.h"
/* Generated */    #define TA_INTERNAL_ERROR(Id) (RetCode.InternalError)
/* Generated */ #elif defined( _RUST )
/* Generated */    #include "ta_defs.h"
/* Generated */    #define TA_INTERNAL_ERROR(Id) (RetCode.InternalError)
/* Generated */ #else
/* Generated */    #include <string.h>
/* Generated */    #include <math.h>
/* Generated */    #include "ta_func.h"
/* Generated */ #endif
/* Generated */ 
/* Generated */ #ifndef TA_UTILITY_H
/* Generated */    #include "ta_utility.h"
/* Generated */ #endif
/* Generated */ 
/* Generated */ #ifndef TA_MEMORY_H
/* Generated */    #include "ta_memory.h"
/* Generated */ #endif
/* Generated */ 
/* Generated */ #define TA_PREFIX(x) TA_##x
/* Generated */ #define INPUT_TYPE   double
/* Generated */ 
/* Generated */ #if defined( _MANAGED )
/* Generated */ int Core::BbandsLookback( int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                         double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                         double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                         MAType        optInMAType ) /* Generated */ 
/* Generated */ #elif defined( _JAVA )
/* Generated */ public int bbandsLookback( int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                          double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                          double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                          MAType        optInMAType ) /* Generated */ 
/* Generated */ #else
/* Generated */ TA_LIB_API int TA_BBANDS_Lookback( int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                             double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                             double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                             TA_MAType     optInMAType ) /* Generated */ 
/* Generated */ #endif
/**** END GENCODE SECTION 1 - DO NOT DELETE THIS LINE ****/
{
   /* insert local variable here */

/**** START GENCODE SECTION 2 - DO NOT DELETE THIS LINE ****/
/* Generated */ #ifndef TA_FUNC_NO_RANGE_CHECK
/* Generated */    /* min/max are checked for optInTimePeriod. */
/* Generated */    if( (int)optInTimePeriod == TA_INTEGER_DEFAULT )
/* Generated */       optInTimePeriod = 5;
/* Generated */    else if( ((int)optInTimePeriod < 2) || ((int)optInTimePeriod > 100000) )
/* Generated */       return -1;
/* Generated */ 
/* Generated */    if( optInNbDevUp == TA_REAL_DEFAULT )
/* Generated */       optInNbDevUp = 2.000000e+0;
/* Generated */    else if( (optInNbDevUp < -3.000000e+37) ||/* Generated */  (optInNbDevUp > 3.000000e+37) )
/* Generated */       return -1;
/* Generated */ 
/* Generated */    if( optInNbDevDn == TA_REAL_DEFAULT )
/* Generated */       optInNbDevDn = 2.000000e+0;
/* Generated */    else if( (optInNbDevDn < -3.000000e+37) ||/* Generated */  (optInNbDevDn > 3.000000e+37) )
/* Generated */       return -1;
/* Generated */ 
/* Generated */    #if !defined(_MANAGED) && !defined(_JAVA)
/* Generated */    if( (int)optInMAType == TA_INTEGER_DEFAULT )
/* Generated */       optInMAType = (TA_MAType)0;
/* Generated */    else if( ((int)optInMAType < 0) || ((int)optInMAType > 8) )
/* Generated */       return -1;
/* Generated */ 
/* Generated */    #endif /* !defined(_MANAGED) && !defined(_JAVA)*/
/* Generated */ #endif /* TA_FUNC_NO_RANGE_CHECK */
/**** END GENCODE SECTION 2 - DO NOT DELETE THIS LINE ****/

   /* insert lookback code here. */
   UNUSED_VARIABLE(optInNbDevUp);
   UNUSED_VARIABLE(optInNbDevDn);

   /* The lookback is driven by the middle band moving average. */
   return LOOKBACK_CALL(MA)( optInTimePeriod, optInMAType );
}

/**** START GENCODE SECTION 3 - DO NOT DELETE THIS LINE ****/
/*
 * TA_BBANDS - Bollinger Bands
 * 
 * Input  = double
 * Output = double, double, double
 * 
 * Optional Parameters
 * -------------------
 * optInTimePeriod:(From 2 to 100000)
 *    Number of period
 * 
 * optInNbDevUp:(From TA_REAL_MIN to TA_REAL_MAX)
 *    Deviation multiplier for upper band
 * 
 * optInNbDevDn:(From TA_REAL_MIN to TA_REAL_MAX)
 *    Deviation multiplier for lower band
 * 
 * optInMAType:
 *    Type of Moving Average
 * 
 * 
 */
/* Generated */ 
/* Generated */ #if defined( _MANAGED ) && defined( USE_SUBARRAY )
/* Generated */ enum class Core::RetCode Core::Bbands( int    startIdx,
/* Generated */                                        int    endIdx,
/* Generated */                                        SubArray<double>^ inReal,
/* Generated */                                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        MAType        optInMAType,
/* Generated */                                        [Out]int%    outBegIdx,
/* Generated */                                        [Out]int%    outNBElement,
/* Generated */                                        SubArray<double>^  outRealUpperBand,
/* Generated */                                        SubArray<double>^  outRealMiddleBand,
/* Generated */                                        SubArray<double>^  outRealLowerBand )
/* Generated */ #elif defined( _MANAGED )
/* Generated */ enum class Core::RetCode Core::Bbands( int    startIdx,
/* Generated */                                        int    endIdx,
/* Generated */                                        cli::array<double>^ inReal,
/* Generated */                                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        MAType        optInMAType,
/* Generated */                                        [Out]int%    outBegIdx,
/* Generated */                                        [Out]int%    outNBElement,
/* Generated */                                        cli::array<double>^  outRealUpperBand,
/* Generated */                                        cli::array<double>^  outRealMiddleBand,
/* Generated */                                        cli::array<double>^  outRealLowerBand )
/* Generated */ #elif defined( _JAVA )
/* Generated */ public RetCode bbands( int    startIdx,
/* Generated */                        int    endIdx,
/* Generated */                        double       inReal[],
/* Generated */                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                        MAType        optInMAType,
/* Generated */                        MInteger     outBegIdx,
/* Generated */                        MInteger     outNBElement,
/* Generated */                        double        outRealUpperBand[],
/* Generated */                        double        outRealMiddleBand[],
/* Generated */                        double        outRealLowerBand[] )
/* Generated */ #else
/* Generated */ TA_LIB_API TA_RetCode TA_BBANDS( int    startIdx,
/* Generated */                                  int    endIdx,
/* Generated */                                             const double inReal[],
/* Generated */                                             int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                             double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                             double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                             TA_MAType     optInMAType,
/* Generated */                                             int          *outBegIdx,
/* Generated */                                             int          *outNBElement,
/* Generated */                                             double        outRealUpperBand[],
/* Generated */                                             double        outRealMiddleBand[],
/* Generated */                                             double        outRealLowerBand[] )
/* Generated */ #endif
/**** END GENCODE SECTION 3 - DO NOT DELETE THIS LINE ****/
{
   /* Insert local variables here. */
   ENUM_DECLARATION(RetCode) retCode;
   int i;
   double tempReal, tempReal2;
   ARRAY_REF(tempBuffer1);
   ARRAY_REF(tempBuffer2);

/**** START GENCODE SECTION 4 - DO NOT DELETE THIS LINE ****/
/* Generated */ 
/* Generated */ #ifndef TA_FUNC_NO_RANGE_CHECK
/* Generated */ 
/* Generated */    /* Validate the requested output range. */
/* Generated */    if( startIdx < 0 )
/* Generated */       return ENUM_VALUE(RetCode,TA_OUT_OF_RANGE_START_INDEX,OutOfRangeStartIndex);
/* Generated */    if( (endIdx < 0) || (endIdx < startIdx))
/* Generated */       return ENUM_VALUE(RetCode,TA_OUT_OF_RANGE_END_INDEX,OutOfRangeEndIndex);
/* Generated */ 
/* Generated */    #if !defined(_JAVA)
/* Generated */    if( !inReal ) return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */    #endif /* !defined(_JAVA)*/
/* Generated */    /* min/max are checked for optInTimePeriod. */
/* Generated */    if( (int)optInTimePeriod == TA_INTEGER_DEFAULT )
/* Generated */       optInTimePeriod = 5;
/* Generated */    else if( ((int)optInTimePeriod < 2) || ((int)optInTimePeriod > 100000) )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    if( optInNbDevUp == TA_REAL_DEFAULT )
/* Generated */       optInNbDevUp = 2.000000e+0;
/* Generated */    else if( (optInNbDevUp < -3.000000e+37) ||/* Generated */  (optInNbDevUp > 3.000000e+37) )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    if( optInNbDevDn == TA_REAL_DEFAULT )
/* Generated */       optInNbDevDn = 2.000000e+0;
/* Generated */    else if( (optInNbDevDn < -3.000000e+37) ||/* Generated */  (optInNbDevDn > 3.000000e+37) )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    #if !defined(_MANAGED) && !defined(_JAVA)
/* Generated */    if( (int)optInMAType == TA_INTEGER_DEFAULT )
/* Generated */       optInMAType = (TA_MAType)0;
/* Generated */    else if( ((int)optInMAType < 0) || ((int)optInMAType > 8) )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    #endif /* !defined(_MANAGED) && !defined(_JAVA)*/
/* Generated */    #if !defined(_JAVA)
/* Generated */    if( !outRealUpperBand )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    if( !outRealMiddleBand )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    if( !outRealLowerBand )
/* Generated */       return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */ 
/* Generated */    #endif /* !defined(_JAVA) */
/* Generated */ #endif /* TA_FUNC_NO_RANGE_CHECK */
/* Generated */ 
/**** END GENCODE SECTION 4 - DO NOT DELETE THIS LINE ****/

   /* Insert TA function code here. */

   /* Identify TWO temporary buffer among the outputs.
    *
    * These temporary buffers allows to perform the
    * calculation without any memory allocation.
    *
    * Whenever possible, make the tempBuffer1 be the
    * middle band output. This will save one copy operation.
    */
   #if defined(USE_SINGLE_PRECISION_INPUT) || defined( USE_SUBARRAY )
      tempBuffer1 = outRealMiddleBand;
      tempBuffer2 = outRealLowerBand;
   #else
      if( inReal == outRealUpperBand )
      {
         tempBuffer1 = outRealMiddleBand;
         tempBuffer2 = outRealLowerBand;
      }
      else if( inReal == outRealLowerBand )
      {
         tempBuffer1 = outRealMiddleBand;
         tempBuffer2 = outRealUpperBand;
      }
      else if( inReal == outRealMiddleBand )
      {
         tempBuffer1 = outRealLowerBand;
         tempBuffer2 = outRealUpperBand;
      }
      else
      {
         tempBuffer1 = outRealMiddleBand;
         tempBuffer2 = outRealUpperBand;
      }
      /* Check that the caller is not doing tricky things.
       * (like using the input buffer in two output!)
       */
      if( (tempBuffer1 == inReal) || (tempBuffer2 == inReal) )
         return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
   #endif


   /* Calculate the middle band, which is a moving average.
    * The other two bands will simply add/substract the
    * standard deviation from this middle band.
    */
   retCode = FUNCTION_CALL(MA)( startIdx, endIdx, inReal,
                                optInTimePeriod, optInMAType,
                                outBegIdx, outNBElement, tempBuffer1 );

   if( (retCode != ENUM_VALUE(RetCode,TA_SUCCESS,Success) ) || ((int)VALUE_HANDLE_DEREF(outNBElement) == 0) )
   {
      VALUE_HANDLE_DEREF_TO_ZERO(outNBElement);
      return retCode;
   }

   /* Calculate the standard deviation into tempBuffer2. */
   if( optInMAType == ENUM_VALUE(MAType,TA_MAType_SMA,Sma) )
   {
      /* A small speed optimization by re-using the
       * already calculated SMA.
       */
       FUNCTION_CALL(INT_stddev_using_precalc_ma)( inReal, tempBuffer1,
                                                   (int)VALUE_HANDLE_DEREF(outBegIdx), (int)VALUE_HANDLE_DEREF(outNBElement),
                                                   optInTimePeriod, tempBuffer2 );
   }
   else
   {
      /* Calculate the Standard Deviation */
      retCode = FUNCTION_CALL(STDDEV)( (int)VALUE_HANDLE_DEREF(outBegIdx), endIdx, inReal,
                                       optInTimePeriod, 1.0,
                                       outBegIdx, outNBElement, tempBuffer2 );

      if( retCode != ENUM_VALUE(RetCode,TA_SUCCESS,Success) )
      {
         VALUE_HANDLE_DEREF_TO_ZERO(outNBElement);
         return retCode;
      }
   }

   /* Copy the MA calculation into the middle band ouput, unless
    * the calculation was done into it already!
    */
   #if !defined(USE_SINGLE_PRECISION_INPUT)
      if( tempBuffer1 != outRealMiddleBand )
      {
         ARRAY_COPY( outRealMiddleBand, tempBuffer1, VALUE_HANDLE_DEREF(outNBElement) );
      }
   #endif

   /* Now do a tight loop to calculate the upper/lower band at
    * the same time.
    *
    * All the following 5 loops are doing the same, except there
    * is an attempt to speed optimize by eliminating uneeded
    * multiplication.
    */
   if( optInNbDevUp == optInNbDevDn )
   {
      if(  optInNbDevUp == 1.0 )
      {
         /* No standard deviation multiplier needed. */
         for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
         {
            tempReal  = tempBuffer2[i];
            tempReal2 = outRealMiddleBand[i];
            outRealUpperBand[i] = tempReal2 + tempReal;
            outRealLowerBand[i] = tempReal2 - tempReal;
         }
      }
      else
      {
         /* Upper/lower band use the same standard deviation multiplier. */
         for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
         {
            tempReal  = tempBuffer2[i] * optInNbDevUp;
            tempReal2 = outRealMiddleBand[i];
            outRealUpperBand[i] = tempReal2 + tempReal;
            outRealLowerBand[i] = tempReal2 - tempReal;
         }
      }
   }
   else if( optInNbDevUp == 1.0 )
   {
      /* Only lower band has a standard deviation multiplier. */
      for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
      {
         tempReal  = tempBuffer2[i];
         tempReal2 = outRealMiddleBand[i];
         outRealUpperBand[i] = tempReal2 + tempReal;
         outRealLowerBand[i] = tempReal2 - (tempReal * optInNbDevDn);
      }
   }
   else if( optInNbDevDn == 1.0 )
   {
      /* Only upper band has a standard deviation multiplier. */
      for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
      {
         tempReal  = tempBuffer2[i];
         tempReal2 = outRealMiddleBand[i];
         outRealLowerBand[i] = tempReal2 - tempReal;
         outRealUpperBand[i] = tempReal2 + (tempReal * optInNbDevUp);
      }
   }
   else
   {
      /* Upper/lower band have distinctive standard deviation multiplier. */
      for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
      {
         tempReal  = tempBuffer2[i];
         tempReal2 = outRealMiddleBand[i];
         outRealUpperBand[i] = tempReal2 + (tempReal * optInNbDevUp);
         outRealLowerBand[i] = tempReal2 - (tempReal * optInNbDevDn);
      }
   }

   return ENUM_VALUE(RetCode,TA_SUCCESS,Success);
}

/**** START GENCODE SECTION 5 - DO NOT DELETE THIS LINE ****/
/* Generated */ 
/* Generated */ #define  USE_SINGLE_PRECISION_INPUT
/* Generated */ #if !defined( _MANAGED ) && !defined( _JAVA )
/* Generated */    #undef   TA_PREFIX
/* Generated */    #define  TA_PREFIX(x) TA_S_##x
/* Generated */ #endif
/* Generated */ #undef   INPUT_TYPE
/* Generated */ #define  INPUT_TYPE float
/* Generated */ #if defined( _MANAGED ) && defined( USE_SUBARRAY )
/* Generated */ enum class Core::RetCode Core::Bbands( int    startIdx,
/* Generated */                                        int    endIdx,
/* Generated */                                        SubArray<float>^ inReal,
/* Generated */                                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        MAType        optInMAType,
/* Generated */                                        [Out]int%    outBegIdx,
/* Generated */                                        [Out]int%    outNBElement,
/* Generated */                                        SubArray<double>^  outRealUpperBand,
/* Generated */                                        SubArray<double>^  outRealMiddleBand,
/* Generated */                                        SubArray<double>^  outRealLowerBand )
/* Generated */ #elif defined( _MANAGED )
/* Generated */ enum class Core::RetCode Core::Bbands( int    startIdx,
/* Generated */                                        int    endIdx,
/* Generated */                                        cli::array<float>^ inReal,
/* Generated */                                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                                        MAType        optInMAType,
/* Generated */                                        [Out]int%    outBegIdx,
/* Generated */                                        [Out]int%    outNBElement,
/* Generated */                                        cli::array<double>^  outRealUpperBand,
/* Generated */                                        cli::array<double>^  outRealMiddleBand,
/* Generated */                                        cli::array<double>^  outRealLowerBand )
/* Generated */ #elif defined( _JAVA )
/* Generated */ public RetCode bbands( int    startIdx,
/* Generated */                        int    endIdx,
/* Generated */                        float        inReal[],
/* Generated */                        int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                        double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                        double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                        MAType        optInMAType,
/* Generated */                        MInteger     outBegIdx,
/* Generated */                        MInteger     outNBElement,
/* Generated */                        double        outRealUpperBand[],
/* Generated */                        double        outRealMiddleBand[],
/* Generated */                        double        outRealLowerBand[] )
/* Generated */ #else
/* Generated */ TA_RetCode TA_S_BBANDS( int    startIdx,
/* Generated */                         int    endIdx,
/* Generated */                         const float  inReal[],
/* Generated */                         int           optInTimePeriod, /* From 2 to 100000 */
/* Generated */                         double        optInNbDevUp, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                         double        optInNbDevDn, /* From TA_REAL_MIN to TA_REAL_MAX */
/* Generated */                         TA_MAType     optInMAType,
/* Generated */                         int          *outBegIdx,
/* Generated */                         int          *outNBElement,
/* Generated */                         double        outRealUpperBand[],
/* Generated */                         double        outRealMiddleBand[],
/* Generated */                         double        outRealLowerBand[] )
/* Generated */ #endif
/* Generated */ {
/* Generated */    ENUM_DECLARATION(RetCode) retCode;
/* Generated */    int i;
/* Generated */    double tempReal, tempReal2;
/* Generated */    ARRAY_REF(tempBuffer1);
/* Generated */    ARRAY_REF(tempBuffer2);
/* Generated */  #ifndef TA_FUNC_NO_RANGE_CHECK
/* Generated */     if( startIdx < 0 )
/* Generated */        return ENUM_VALUE(RetCode,TA_OUT_OF_RANGE_START_INDEX,OutOfRangeStartIndex);
/* Generated */     if( (endIdx < 0) || (endIdx < startIdx))
/* Generated */        return ENUM_VALUE(RetCode,TA_OUT_OF_RANGE_END_INDEX,OutOfRangeEndIndex);
/* Generated */     #if !defined(_JAVA)
/* Generated */     if( !inReal ) return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     #endif 
/* Generated */     if( (int)optInTimePeriod == TA_INTEGER_DEFAULT )
/* Generated */        optInTimePeriod = 5;
/* Generated */     else if( ((int)optInTimePeriod < 2) || ((int)optInTimePeriod > 100000) )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     if( optInNbDevUp == TA_REAL_DEFAULT )
/* Generated */        optInNbDevUp = 2.000000e+0;
/* Generated */     else if( (optInNbDevUp < -3.000000e+37) ||  (optInNbDevUp > 3.000000e+37) )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     if( optInNbDevDn == TA_REAL_DEFAULT )
/* Generated */        optInNbDevDn = 2.000000e+0;
/* Generated */     else if( (optInNbDevDn < -3.000000e+37) ||  (optInNbDevDn > 3.000000e+37) )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     #if !defined(_MANAGED) && !defined(_JAVA)
/* Generated */     if( (int)optInMAType == TA_INTEGER_DEFAULT )
/* Generated */        optInMAType = (TA_MAType)0;
/* Generated */     else if( ((int)optInMAType < 0) || ((int)optInMAType > 8) )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     #endif 
/* Generated */     #if !defined(_JAVA)
/* Generated */     if( !outRealUpperBand )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     if( !outRealMiddleBand )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     if( !outRealLowerBand )
/* Generated */        return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */     #endif 
/* Generated */  #endif 
/* Generated */    #if defined(USE_SINGLE_PRECISION_INPUT) || defined( USE_SUBARRAY )
/* Generated */       tempBuffer1 = outRealMiddleBand;
/* Generated */       tempBuffer2 = outRealLowerBand;
/* Generated */    #else
/* Generated */       if( inReal == outRealUpperBand )
/* Generated */       {
/* Generated */          tempBuffer1 = outRealMiddleBand;
/* Generated */          tempBuffer2 = outRealLowerBand;
/* Generated */       }
/* Generated */       else if( inReal == outRealLowerBand )
/* Generated */       {
/* Generated */          tempBuffer1 = outRealMiddleBand;
/* Generated */          tempBuffer2 = outRealUpperBand;
/* Generated */       }
/* Generated */       else if( inReal == outRealMiddleBand )
/* Generated */       {
/* Generated */          tempBuffer1 = outRealLowerBand;
/* Generated */          tempBuffer2 = outRealUpperBand;
/* Generated */       }
/* Generated */       else
/* Generated */       {
/* Generated */          tempBuffer1 = outRealMiddleBand;
/* Generated */          tempBuffer2 = outRealUpperBand;
/* Generated */       }
/* Generated */       if( (tempBuffer1 == inReal) || (tempBuffer2 == inReal) )
/* Generated */          return ENUM_VALUE(RetCode,TA_BAD_PARAM,BadParam);
/* Generated */    #endif
/* Generated */    retCode = FUNCTION_CALL(MA)( startIdx, endIdx, inReal,
/* Generated */                                 optInTimePeriod, optInMAType,
/* Generated */                                 outBegIdx, outNBElement, tempBuffer1 );
/* Generated */    if( (retCode != ENUM_VALUE(RetCode,TA_SUCCESS,Success) ) || ((int)VALUE_HANDLE_DEREF(outNBElement) == 0) )
/* Generated */    {
/* Generated */       VALUE_HANDLE_DEREF_TO_ZERO(outNBElement);
/* Generated */       return retCode;
/* Generated */    }
/* Generated */    if( optInMAType == ENUM_VALUE(MAType,TA_MAType_SMA,Sma) )
/* Generated */    {
/* Generated */        FUNCTION_CALL(INT_stddev_using_precalc_ma)( inReal, tempBuffer1,
/* Generated */                                                    (int)VALUE_HANDLE_DEREF(outBegIdx), (int)VALUE_HANDLE_DEREF(outNBElement),
/* Generated */                                                    optInTimePeriod, tempBuffer2 );
/* Generated */    }
/* Generated */    else
/* Generated */    {
/* Generated */       retCode = FUNCTION_CALL(STDDEV)( (int)VALUE_HANDLE_DEREF(outBegIdx), endIdx, inReal,
/* Generated */                                        optInTimePeriod, 1.0,
/* Generated */                                        outBegIdx, outNBElement, tempBuffer2 );
/* Generated */       if( retCode != ENUM_VALUE(RetCode,TA_SUCCESS,Success) )
/* Generated */       {
/* Generated */          VALUE_HANDLE_DEREF_TO_ZERO(outNBElement);
/* Generated */          return retCode;
/* Generated */       }
/* Generated */    }
/* Generated */    #if !defined(USE_SINGLE_PRECISION_INPUT)
/* Generated */       if( tempBuffer1 != outRealMiddleBand )
/* Generated */       {
/* Generated */          ARRAY_COPY( outRealMiddleBand, tempBuffer1, VALUE_HANDLE_DEREF(outNBElement) );
/* Generated */       }
/* Generated */    #endif
/* Generated */    if( optInNbDevUp == optInNbDevDn )
/* Generated */    {
/* Generated */       if(  optInNbDevUp == 1.0 )
/* Generated */       {
/* Generated */          for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
/* Generated */          {
/* Generated */             tempReal  = tempBuffer2[i];
/* Generated */             tempReal2 = outRealMiddleBand[i];
/* Generated */             outRealUpperBand[i] = tempReal2 + tempReal;
/* Generated */             outRealLowerBand[i] = tempReal2 - tempReal;
/* Generated */          }
/* Generated */       }
/* Generated */       else
/* Generated */       {
/* Generated */          for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
/* Generated */          {
/* Generated */             tempReal  = tempBuffer2[i] * optInNbDevUp;
/* Generated */             tempReal2 = outRealMiddleBand[i];
/* Generated */             outRealUpperBand[i] = tempReal2 + tempReal;
/* Generated */             outRealLowerBand[i] = tempReal2 - tempReal;
/* Generated */          }
/* Generated */       }
/* Generated */    }
/* Generated */    else if( optInNbDevUp == 1.0 )
/* Generated */    {
/* Generated */       for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
/* Generated */       {
/* Generated */          tempReal  = tempBuffer2[i];
/* Generated */          tempReal2 = outRealMiddleBand[i];
/* Generated */          outRealUpperBand[i] = tempReal2 + tempReal;
/* Generated */          outRealLowerBand[i] = tempReal2 - (tempReal * optInNbDevDn);
/* Generated */       }
/* Generated */    }
/* Generated */    else if( optInNbDevDn == 1.0 )
/* Generated */    {
/* Generated */       for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
/* Generated */       {
/* Generated */          tempReal  = tempBuffer2[i];
/* Generated */          tempReal2 = outRealMiddleBand[i];
/* Generated */          outRealLowerBand[i] = tempReal2 - tempReal;
/* Generated */          outRealUpperBand[i] = tempReal2 + (tempReal * optInNbDevUp);
/* Generated */       }
/* Generated */    }
/* Generated */    else
/* Generated */    {
/* Generated */       for( i=0; i < (int)VALUE_HANDLE_DEREF(outNBElement); i++ )
/* Generated */       {
/* Generated */          tempReal  = tempBuffer2[i];
/* Generated */          tempReal2 = outRealMiddleBand[i];
/* Generated */          outRealUpperBand[i] = tempReal2 + (tempReal * optInNbDevUp);
/* Generated */          outRealLowerBand[i] = tempReal2 - (tempReal * optInNbDevDn);
/* Generated */       }
/* Generated */    }
/* Generated */    return ENUM_VALUE(RetCode,TA_SUCCESS,Success);
/* Generated */ }
/* Generated */ 
/* Generated */ #if defined( _MANAGED )
/* Generated */ }}} // Close namespace TicTacTec.TA.Lib
/* Generated */ #endif
/**** END GENCODE SECTION 5 - DO NOT DELETE THIS LINE ****/

