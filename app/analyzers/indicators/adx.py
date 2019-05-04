
import pandas
import os
import numpy
import matplotlib.pyplot as plt
from pandas.plotting import table

class Adx():
    def analyze(self, historical_data, signal=["adx"], hot_thresh=None, cold_thresh=None):
        """
        strength of a trend
        ADX > 25 = strength
        ADX < 20 = weak or trendless
        ------
        0-25    absent or weak trend
        25-50   strong trend
        50-75   very strong trend
        75-100  extremely strong trend
        """
        #dataframe = self.convert_to_dataframe(historical_data)
        dataframe = historical_data

        adx_columns = {
            'tr': [numpy.nan] * dataframe.index.shape[0],
            'atr': [numpy.nan] * dataframe.index.shape[0],
            'pdm': [numpy.nan] * dataframe.index.shape[0],
            'ndm': [numpy.nan] * dataframe.index.shape[0],
            'pdm_smooth': [numpy.nan] * dataframe.index.shape[0],
            'ndm_smooth': [numpy.nan] * dataframe.index.shape[0],
            'ndi': [numpy.nan] * dataframe.index.shape[0],
            'pdi': [numpy.nan] * dataframe.index.shape[0],
            'dx': [numpy.nan] * dataframe.index.shape[0],
            'adx': [numpy.nan] * dataframe.index.shape[0]
        }

        adx_values = pandas.DataFrame(adx_columns,
                                      index=dataframe.index
                                      )

        period = 14
        adx_values['tr'] = self.TR(dataframe['high'],
                                   dataframe['low'],
                                   dataframe['close'],
                                   adx_values['tr']
                                   )
        adx_values['pdm'], adx_values['ndm'] = self.DM(dataframe['high'],
                                                       dataframe['low'],
                                                       adx_values['pdm'],
                                                       adx_values['ndm']
                                                       )
        adx_values['pdm_smooth'], adx_values['ndm_smooth'] = self.DMsmooth(adx_values['pdm'],
                                                                           adx_values['ndm'],
                                                                           adx_values['pdm_smooth'],
                                                                           adx_values['ndm_smooth'],
                                                                           period
                                                                           )
        adx_values['pdi'], adx_values['ndi'] = self.DI(adx_values['pdm_smooth'],
                                                       adx_values['ndm_smooth'],
                                                       adx_values['tr'],
                                                       adx_values['pdi'],
                                                       adx_values['ndi']
                                                       )
        adx_values['atr'] = self.ATR(adx_values['tr'],
                                     adx_values['atr'],
                                     period
                                     )
        adx_values['dx'], adx_values['adx'] = self.ADX(adx_values['pdi'],
                                                       adx_values['ndi'],
                                                       adx_values['dx'],
                                                       adx_values['adx'],
                                                       period
                                                       )


        '''
        if obv_values[signal[0]].shape[0]:
            adx_values['is_hot'] = rsi_values[signal[0]] < hot_thresh
            rsi_values['is_cold'] = rsi_values[signal[0]] > cold_thresh
        '''

        return adx_values


    def TR(self, high, low, close, tr):
        """
        TR (True Range)
        :param high:
        :param low:
        :param close:
        :param tr:
        :return:
        """

        tr[0] = abs(high[0] - low[0])
        for index in range(1, tr.shape[0]):
            x = high[index] - close[index]
            y = abs(high[index] - close[index - 1])
            z = abs(low[index] - close[index - 1])
            tr[index] = max(x, y, z)

        return tr


    def DM(self, high, low, pdm, ndm):
        """
        DM (Directional Movement)
        :param high:
        :param low:
        :param pdm:
        :param ndm:
        :return:
        """

        for index in range(1, high.shape[0]):
            up_move = high[index] - high[index-1]
            down_move = low[index-1] - low[index]

            if up_move > down_move and up_move > 0:
                pdm[index] = up_move
            else:
                pdm[index] = 0
            if down_move > up_move and down_move > 0:
                ndm[index] = down_move
            else:
                ndm[index] = 0

        return pdm, ndm

    def DMsmooth(self, pdm, ndm, pdm_smooth, ndm_smooth, period):
        """

        :param pdm:
        :param ndm:
        :param pdm_smooth:
        :param ndm_smooth:
        :param period:
        :return:
        """

        pdm_smooth[period-1] = pdm[0:period].sum() / period
        ndm_smooth[period - 1] = ndm[0:period].sum() / period

        for index in range(period, pdm.shape[0]):
            pdm_smooth[index] = (pdm[index-1] - (pdm_smooth[index-1]/period)) + pdm_smooth[index-1]
            ndm_smooth[index] = (ndm[index - 1] - (ndm_smooth[index-1] / period)) + ndm_smooth[index-1]

        return pdm_smooth, ndm_smooth


    def DI(self, pdm_smooth, ndm_smooth, tr, pdi, ndi):
        """
        DI (Directional Movement Indicator)
        :param pdm_smooth:
        :param ndm_smooth:
        :param tr:
        :param pdi:
        :param ndi:
        :return:
        """
        for index in range(0, tr.shape[0]):
            pdi[index] = (pdm_smooth[index] / tr[index]) * 100
            ndi[index] = (ndm_smooth[index] / tr[index]) * 100

        return pdi, ndi


    def ATR(self, tr, atr, period):
        """
        Uses WILDER'S SMOOTHING METHOD
        ATR = a*TR + (1-a)* ATR_1
        a = (1/n)
        :param tr:
        :param atr:
        :param period:
        :return:
        """
        atr[period-1] = tr[0:period].sum() / period

        for index in range(period, tr.shape[0]):
            atr[index] = ((atr[index-1] * (period - 1)) + tr[index]) / period

        return atr

    def ADX(self, pdi, ndi, dx, adx, period):
        """

        :param pdi:
        :param ndi:
        :param dx:
        :param adx:
        :param period:
        :return:
        """
        for index in range(0, pdi.shape[0]):
            dx[index] = ((abs(pdi[index] - ndi[index])) / (abs(pdi[index] + ndi[index]))) * 100

        period2 = period*2
        adx[period2-1] = dx[period:period2].sum() / period
        for index in range(period2, dx.shape[0]):
            adx[index] = ((adx[index-1] * (period - 1)) + dx[index]) / period

        return dx, adx


    def create_chart(self, dataframe):
        x = dataframe.index
        y = dataframe['adx']
        plt.plot(x, y)
        plt.show()

if __name__ == '__main__':
    hist = pandas.read_csv(r'savefunctiondata')
    hist = hist.set_index(pandas.to_datetime(hist['datetime']))
    hist.drop('datetime', axis=1, inplace=True)
    adx = Adx()
    data = adx.analyze(historical_data=hist)
    #data.to_csv('dmtest1', columns=['dx'], sep=' ')
    data.to_csv('dmtest1', columns= ['dx', 'adx'], sep=',')
    adx.create_chart(data)

