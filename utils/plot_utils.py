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


def plot_roc_by_masks(data, target_col, score_col, masks_dict, 
                     figsize=(8, 4), palette='bright', 
                     title='ROC-кривые по различным подвыборкам',
                     ax=None,
                     save_path=None):
    """
    Рисует ROC-кривые для различных подвыборок данных
    """
    
    # Генерируем цвета
    colors = sns.color_palette(palette, len(masks_dict))
    
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    results = {}
    
    for i, (mask_name, mask) in enumerate(masks_dict.items()):
        # Применяем маску
        subset = data[mask]
        y_true = subset[target_col]
        y_pred = subset[score_col]
        
        # Расчет ROC-кривой
        fpr, tpr, thresholds = roc_curve(y_true, y_pred)
        roc_auc = auc(fpr, tpr)
        
        # Сохраняем результаты
        results[mask_name] = {
            'auc': roc_auc,
            'sample_size': len(subset),
            'positive_rate': y_true.mean()
        }
        
        # Рисуем кривую
        ax.plot(fpr, tpr, color=colors[i], lw=1, 
                label=f'{mask_name} (AUC = {roc_auc:.3f}, n={len(subset)})')
    
    # Базовая линия (случайный классификатор)
    ax.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', 
             alpha=0.7, label='Случайный классификатор')
    
    # Настройки графика
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold', labelpad=20)
    ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold', labelpad=20)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=20)

    # Сетка и легенда
    ax.grid(True, alpha=0.6, color='white')
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_facecolor('0.95')
    
    # Улучшаем внешний вид
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if save_path and ax is None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # return fig, ax, results

def plot_gini_by_period_styled(data, gini_col, period_col, 
                              figsize=(8, 4), 
                              target_gini=40,
                              title='Динамика Gini по периодам',
                              ax=None,
                              save_path=None):
    """
    Стильная версия графика Gini по периодам
    """
    
    # plt.style.use('seaborn-v0_8')s
    # plt.style.use('default')
    
    if isinstance(data[period_col].dtype, pd.PeriodDtype):
        data[period_col] = data[period_col].astype(str)

    data[gini_col] *= 100
    data_sorted = data.sort_values(period_col).copy()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    # Создаем градиентный цвет от синего к красному в зависимости от значения Gini
    colors = plt.cm.RdYlBu_r((data_sorted[gini_col] - data_sorted[gini_col].min()) / 
                            (data_sorted[gini_col].max() - data_sorted[gini_col].min()))
    
    # Рисуем линию
    line = ax.plot(data_sorted[period_col], data_sorted[gini_col], 
                  color='#2E86AB', linewidth=3, alpha=0.8, 
                  marker='o', markersize=8, markerfacecolor='white',
                  markeredgecolor='#2E86AB', markeredgewidth=2)[0]
    
    # Заливка под кривой
    ax.fill_between(data_sorted[period_col], data_sorted[gini_col], 
                   alpha=0.2, color='#2E86AB')
    
    # Линия целевого уровня
    if target_gini is not None:
        target_line = ax.axhline(y=target_gini, color='#E74C3C', linestyle='--', 
                               linewidth=2.5, alpha=0.9, 
                               label=f'Целевой Gini ({target_gini}%)')
    
    # Аннотации значений
    for i, (period, gini) in enumerate(zip(data_sorted[period_col], data_sorted[gini_col])):
        color = '#E74C3C' if gini < target_gini else '#27AE60'
        ax.annotate(f'{gini:.1f}%', 
                   xy=(period, gini), 
                   xytext=(0, 15),
                   textcoords='offset points',
                   ha='center', va='bottom',
                   fontsize=10, fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor=color, alpha=0.9))
    
    # Настройки графика
    ax.set_xlabel('Период', fontsize=12, fontweight='bold', labelpad=20)
    ax.set_ylabel('Gini коэффициент, %', fontsize=12, fontweight='bold', labelpad=20)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
    
    ax.set_ylim([0.0, 100.0])

    # Сетка и легенда
    ax.grid(True, alpha=0.6, color='white')
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_facecolor('0.95')
    
    # Убираем рамки
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Поворачиваем подписи периодов для лучшей читаемости
    ax.tick_params(axis='x', rotation=45)
    
    if save_path and ax is None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    
    # return fig, ax