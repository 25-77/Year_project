import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve, auc


def time_ranges_plot(datas_dict, date_column, save_path=None):
    """
    Функция для построения графика временных диапазонов.
    
    Parameters:
    ----------
    datas_dict : dict
        Словарь, где ключи - названия датасетов, значения - датафреймы с колонкой date_column.
    date_column : str
        Название колонки с датами в формате 'YYYYMM'.
        
    """
    plt.figure(figsize=(16, 1))

    for data in datas_dict.keys():
        months = sorted(map(str, datas_dict[data][date_column].unique()))

        if len(months) > 1:
            plt.plot(months, [data for x in months], lw=5)
        else:
            plt.scatter(months, [data for x in months], linewidths=5, marker='_')
    
    plt.xticks(rotation=90)
    plt.tick_params(labelsize=14, axis='y')
    plt.title('Рассматриваемые временные диапазоны:', fontdict={'fontsize':15})
    plt.tight_layout()

    # Сохраняем ДО показа
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)

    # plt.show()

    return