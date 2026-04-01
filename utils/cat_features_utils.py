import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

def preparing_cat_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Функция для преобразрвания категориальных признаков
    """
    
    # идея преобразований своя. 
    # словари и условия для объединения категорий - deepseek
    
    # заполнение пропусков категорией missing
    fill_cat_cols  = ['ProductCD', 'card4', 'card6', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
                      'id_12', 'id_15', 'id_16', 'id_23', 'id_27', 'id_28', 'id_29', 'id_30', 'id_31', 'id_33',
                      'id_34', 'id_35', 'id_36', 'id_37', 'id_38', 'DeviceType', 'DeviceInfo', 'P_emaildomain', 'R_emaildomain']
    
    
    # fillna 'missing'
    for col in fill_cat_cols:
        data[f'{col}_new'] = data[col].fillna('missing')
    
    
    ## 'P_emaildomain', 'R_emaildomain'
    # Словарь для группировки email доменов
    email_mapping = {
        # Google
        'gmail.com': 'google',
        'gmail': 'google',
        'googlemail.com': 'google',
        
        # Microsoft
        'hotmail.com': 'microsoft',
        'outlook.com': 'microsoft',
        'live.com': 'microsoft',
        'live.com.mx': 'microsoft',
        'msn.com': 'microsoft',
        'hotmail.fr': 'microsoft',
        'hotmail.de': 'microsoft',
        'hotmail.co.uk': 'microsoft',
        'hotmail.es': 'microsoft',
        'outlook.es': 'microsoft',
        
        # Yahoo
        'yahoo.com': 'yahoo',
        'yahoo.com.mx': 'yahoo',
        'yahoo.co.jp': 'yahoo',
        'ymail.com': 'yahoo',
        'rocketmail.com': 'yahoo',
        'yahoo.fr': 'yahoo', 
        'yahoo.de': 'yahoo',
        'yahoo.es': 'yahoo',
        'yahoo.co.uk': 'yahoo',
        
        # AOL
        'aol.com': 'aol',
        'aim.com': 'aol',
        
        # Apple
        'icloud.com': 'apple',
        'me.com': 'apple',
        'mac.com': 'apple',
        
        # Провайдеры США
        'att.net': 'us_provider',
        'verizon.net': 'us_provider',
        'comcast.net': 'us_provider',
        'charter.net': 'us_provider',
        'cox.net': 'us_provider',
        'optonline.net': 'us_provider',
        'sbcglobal.net': 'us_provider',
        'bellsouth.net': 'us_provider',
        'juno.com': 'us_provider',
        'embarqmail.com': 'us_provider',
        
        # Европейские other
        'gmx.de': 'europe_provider',
        'web.de': 'europe_provider',
        'live.fr': 'europe_provider',
        
        'missing': 'missing'}

    #'P_emaildomain', 'R_emaildomain'
    # 
    data['P_emaildomain_grouped'] = data['P_emaildomain_new'].map(email_mapping).fillna('other')
    data['R_emaildomain_grouped'] = data['R_emaildomain_new'].map(email_mapping).fillna('other')
    
    
    ## id_30
    conditions = [
        data['id_30_new'].str.contains('windows|win10|win7|win8|winxp|winvista|win', na=False),
        data['id_30_new'].str.contains('mac os|macos|macintosh|os x|mac', na=False),
        data['id_30_new'].str.contains('ios|iphone|ipad|ipod', na=False),
        data['id_30_new'].str.contains('android', na=False),
        data['id_30_new'].str.contains('linux|ubuntu|debian|fedora|centos', na=False),
        data['id_30_new'].str.contains('chrome os|chrome', na=False),
        data['id_30_new'].str.contains('missing', na=False)]   

    choices = ['windows', 'mac', 'ios', 'android', 'linux', 'chrome_os', 'missing']

    data['id_30_grouped'] = np.select(conditions, choices, default='other')


    ## id 31
    # Условия для группировки браузеров
    conditions = [
        data['id_31_new'].str.contains('chrome|crm', na=False),
        data['id_31_new'].str.contains('safari|mobile safari', na=False),
        data['id_31_new'].str.contains('firefox|fxios', na=False),
        data['id_31_new'].str.contains('edge|edg', na=False),
        data['id_31_new'].str.contains('ie|internet explorer|trident', na=False),
        data['id_31_new'].str.contains('samsung|samsung browser', na=False),
        data['id_31_new'].str.contains('opera|opr', na=False),
        data['id_31_new'].str.contains('android webview', na=False),
        data['id_31_new'].str.contains('missing', na=False),
    ]

    choices = ['chrome', 'safari', 'firefox', 'edge', 'ie', 'samsung', 'opera', 'android_webview', 'missing']

    data['id_31_grouped'] = np.select(conditions, choices, default='other')
    
    
    ## id_33
    # 
    def get_ratio(res):
        if res == 'missing':
            return 'missing'
        
        try:
            w, h = map(int, str(res).split('x'))
            ratio = round(w / h, 2)
            
            if ratio == 1.33 or ratio == 1.34:
                return '4:3'
            elif ratio == 1.25:
                return '5:4'
            elif ratio == 1.6:
                return '16:10'
            elif ratio == 1.78:
                return '16:9'
            elif ratio == 2.0: 
                return '2:1'
            elif ratio > 2.0:
                return 'ultrawide'
            else:
                return 'other'
        except:
            return 'other'

    #
    data['id_33_ratio'] = data['id_33_new'].apply(get_ratio)
    
    
    ## DeviceInfo

    # Условия для определения бренда
    conditions = [
        data['DeviceInfo_new'].str.contains('ilium', case=False, na=False),
        data['DeviceInfo_new'].str.contains('pixel', case=False, na=False),
        data['DeviceInfo_new'].str.contains('khisense|hisense', case=False, na=False),
        data['DeviceInfo_new'].str.contains('kffowi|kfdowi|kfgiwi|kindle|fire', case=False, na=False),
        data['DeviceInfo_new'].str.contains('trident|trident-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('rv|rv:|rv-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('nexus|nex-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('redmi|red-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('asus', case=False, na=False),
        data['DeviceInfo_new'].str.contains('samsung|sm-|gt-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('iphone|ipad|ipod|ios|android', case=False, na=False),
        data['DeviceInfo_new'].str.contains('lg|lg-|vs5012|vs995|vs988|vs425pp|vs987', case=False, na=False),
        data['DeviceInfo_new'].str.contains('moto|motorola|xt|mot-', case=False, na=False),
        data['DeviceInfo_new'].str.contains('huawei|cam-|hi6210sft', case=False, na=False),
        data['DeviceInfo_new'].str.contains('lenovo', case=False, na=False),
        data['DeviceInfo_new'].str.contains('sony|lt|f3213|f3113|f5121|f3313|f3213|f3113|f3111|g3313|g3223|f8331|f5321|e6603|e5506|e2306|d6603|e5823|c6906', case=False, na=False),
        data['DeviceInfo_new'].str.contains('htc', case=False, na=False),
        data['DeviceInfo_new'].str.contains('blade|zte|m4 ss4456|m4 ss|z981|z835', case=False, na=False),
        data['DeviceInfo_new'].str.contains('alcatel|5080a|5010g|8050g|5025g|5015a|5056a|5012g|5011a', case=False, na=False),
        data['DeviceInfo_new'].str.contains('windows nt|windows|macos|linux', case=False, na=False),
        data['DeviceInfo_new'].str.contains('missing', case=False, na=False),
        ]

    choices = ['ilium', 'pixel', 'hisense', 'amazon', 'trident', 'rv', 'nexus', 'redmi',
               'asus', 'samsung', 'mobile_t', 'lg', 'motorola', 'huawei',
               'lenovo', 'sony', 'htc', 'zte', 'alcatel', 'desktop_os', 'missing']

    data['DeviceInfo_brand'] = np.select(conditions, choices, default='other')
    
    
    return data


