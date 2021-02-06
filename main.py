from pymatgen.core.composition import Composition
from element_recognition import get_ratio, make_compositions
from math import isclose
import pandas as pd
import numpy as np
import PySimpleGUI as sg
import os

class WeighingCalculator:
    def __init__(self, materials):
        '''
        Parameters
        ----------
        materials : list
            [description]
        '''
        self.materials = materials
        self.dict_materials = {material: Composition(material) for material in materials}

    def calc(self, products = [], ratio = [], mg = 2000, excess = {}, match_all = True, progress_bar = True):
        '''
        calculate weighing

        Parameters
        ----------
        products : list, optional
            [description], by default []
        ratio : list, optional
            [description], by default []
        mg : int, optional
            完成量, by default 2000
        excess : dict, optional
            過剰量 e.g. {'Li2O': 0.05}, by default {}
        match_all : bool, optional
            完全一致していないとダメかどうか, by default True
        progress_bar : bool, optional
            進捗バーを表示するかどうか, by default True

        Raises
        ------
        ValueError
        '''
        if len(products) * len(ratio):  # 両方に入力があったら．
            raise ValueError('You can only enter either "products" or "ratio".')
        elif len(products):
            self.df_ratio = get_ratio(materials=self.materials, products = products, match_all = match_all)
        elif len(ratio):
            products = make_compositions(self.materials, ratio = ratio).index.to_numpy().tolist()
            if isinstance(ratio, pd.DataFrame):
                ratio = ratio.loc[:, self.materials].to_numpy()
            elif isinstance(ratio, (pd.Series, np.ndarray, list)):
                ratio = np.array(ratio).reshape(-1, len(self.materials))
            self.df_ratio = pd.DataFrame(ratio, columns = self.materials, index = products)
        else:
            raise ValueError('You have to enter either "products" or "ratio".')

        # 比率が計算できなかった組成をためておくリスト
        # comp_null = []
        
        products = self.df_ratio.index.to_numpy().tolist()  # self.df_ratioではproductsの空白を削除した組成名を得られるため，上書き．
        self.dict_products = {product: Composition(product) for product in products}
        self.products = products

        self.excess = excess

        # 結果を足すSeries
        srs_material_weight = []
        srs_material_weight_excess = []

        # moleをとっておくリスト
        self.moles = []

        # dataframeを各行ごとに取り出す．
        for product, ratio in self.df_ratio.iterrows():
            mole = mg / self.dict_products[product].weight
            self.moles.append(mole)
            if ratio.isnull().all():    # anyのほうが良い気もする．
                pass
            else:   # きちんと計算できていたら
                sr_material_weight = pd.Series(ratio * mole * np.array([self.dict_materials[material].weight for material in self.materials]), index = self.materials, name = product)

                # 過剰量の計算
                sr_material_weight_excess = sr_material_weight.copy()
                for material, excess_ratio in self.excess.items():
                    sr_material_weight_excess[material] *= (1 + excess_ratio)

                srs_material_weight.append(sr_material_weight.to_frame().transpose())
                srs_material_weight_excess.append(sr_material_weight_excess.to_frame().transpose())
        self.df_material_weight = pd.concat(srs_material_weight, axis = 0, sort = False)
        self.df_material_weight_excess = pd.concat(srs_material_weight_excess, axis = 0, sort = False)


class gui:
    def __init__(self, theme = 'SystemDefault'):
        '''
        theme: 'SystemDefault' or 'Black'
        '''
        sg.theme(theme)

        self.font_default = 'Hiragino Sans CNS'
        self.font_size_default = 20
        self.option_text_default = {
            'font': (self.font_default, self.font_size_default),
        }

        self.APP_NAME = '秤量計算ソフト'
         

    def run(self):
        # オブジェクトの生成
        menu_n_materials = Menu(self)

        # layoutの作成
        menu_n_materials.layout = [
            [sg.Text('Start Menu', font = (self.font_default, 25))],
            [sg.Text('')],
            [sg.Text('原料の数'), sg.InputText(key = 'n_materials', size = (3, 1), justification='right')],
            [sg.Text('')],
            [sg.Submit('Next')]
        ]

        # windowの生成
        menu_n_materials.make_window()
        while True:
            menu_n_materials.read()
            if menu_n_materials.event is None:
                # windowを閉じて抜ける
                menu_n_materials.window.close()
                break
            elif menu_n_materials.event == 'Next':
                n_materials = menu_n_materials.values['n_materials']
                try:
                    n_materials = int(n_materials)
                except ValueError:
                    popup_error = sg.popup_error('You have to enter an integer.', **self.option_text_default, modal = False, keep_on_top=True)
                else:
                    # windowを閉じてから次のwindowを開く
                    menu_n_materials.window.close()
                    self._get_materials_compositions(n_materials)
                    break
                

    def _get_materials_compositions(self, n_materials):
        # オブジェクトの生成
        get_materials_compositions = Menu(self)

        # 原料を入力するやつ
        entering_compositions_layout = [[sg.Text('原料{}'.format(n+1), size = (6, 1)), sg.InputText(size = (10, 1), key = 'material{}'.format(n+1))] for n in range(n_materials)]

        # このページのlayoutの作成
        if n_materials > 5: # 数が多いときはスクロールできるように．
            get_materials_compositions.layout = [
                [sg.Column(entering_compositions_layout, scrollable = True, vertical_scroll_only=True, size = (400, 225), justification='center')],
            ]
        else:
            get_materials_compositions.layout = entering_compositions_layout
        # buttonとタイトルは共通なので足す．
        get_materials_compositions.layout.insert(0, [sg.Text('出発物質入力画面')])
        get_materials_compositions.layout.extend([[sg.Text('')], [sg.Submit('Confirm')]])

        # windowの生成
        get_materials_compositions.make_window()
        while True:
            # read
            get_materials_compositions.read()
            if get_materials_compositions.event is None:
                # windowを閉じて抜ける
                get_materials_compositions.window.close()
                break
            elif get_materials_compositions.event == 'Confirm':
                dict_materials = {k:v for k, v in get_materials_compositions.values.items() if 'material' in k}
                if '' in dict_materials.values():
                    sg.popup_error('Some of them are not filled in at all.', **self.option_text_default, modal = False, keep_on_top=True)
                    continue
                # windowを閉じてから次のwindowを開く
                get_materials_compositions.window.close()
                self._calculation_menu(dict_materials)
                break


    def _calculation_menu(self, dict_materials):
        calculation_menu = Menu(self)

        n_materials = len(dict_materials)

        # これから定義する二つのフレームを同じように整えるoptions
        options_frame = {
            'border_width':0,
            'element_justification':'center',
            'size' : (300, 200)
        }

        # 原料比を入力するやつ
        layout_entering_ratio = [[sg.Text(dict_materials['material{}'.format(n+1)], size = (6, 1)), sg.InputText(size = (6, 1), key = dict_materials['material{}'.format(n+1)], justification='right')] for n in range(n_materials)]

        # ratio
        options_layout_ratio = {
            'size': (220, 170),
            'justification': 'center'
        }
        if n_materials > 5: # スクロールできるように．
            layout_ratio = [
                [sg.Column(layout_entering_ratio, scrollable = True, vertical_scroll_only=True, **options_layout_ratio)],
            ]
        else:
            layout_ratio = layout_entering_ratio
        # buttonは共通なので足す．
        layout_ratio.extend([[sg.Text('')], [sg.Submit('Calc (ratio)', key = 'Calc_ratio')]])

        frame_ratio = sg.Frame('', layout = layout_ratio, **options_frame)

        # 生成物を入力するやつ
        layout_product = [
            [sg.Text('生成物を入力する場合')],
            [sg.InputText(size = (15, 1), key = 'product')],
            [sg.Text('')],
            [sg.Submit('Calc (Composition)', key = 'Calc_product')],
        ]
        frame_product = sg.Frame('', layout = layout_product,  **{k:v for k, v in options_frame.items() if k != 'border_widht'})

        # 過剰量を入力するやつ
        layout_excess = [[sg.Text(dict_materials['material{}'.format(n+1)], size = (6, 1)), sg.InputText('0.00', key = '{}_excess'.format(dict_materials['material{}'.format(n+1)]), size = (7, 1), justification='right'), sg.Text('mol%')] for n in range(n_materials)]
        if n_materials > 5: # スクロールできるように
            layout_excess = [[sg.Column(layout_excess, scrollable=True, vertical_scroll_only=True, justification='center')]]
        # layout_excess.insert(0, [sg.Text('過剰量', justification='center')])
            
        frame_excess = sg.Frame('過剰量', layout = layout_excess, **{k:v for k, v in options_frame.items() if k != 'border_width'})

        # 完成量を入力するやつ
        layout_mg = [
            [sg.Text('理論完成量（過剰量を含まない）')],
            [sg.InputText('2000', key = 'mg', size = (7, 1), justification='right'), sg.Text('mg')]
        ]
        frame_mg = sg.Frame('', layout=layout_mg, **options_frame)

        # このページ全体のlayout
        calculation_menu.layout = [
            [sg.Text('秤量計算画面')],
            [frame_mg],
            [sg.Text('')],
            [frame_ratio, frame_product],
            [sg.Text('_'*100)],
            [sg.Text('共通の設定', justification='left')],
            [frame_excess]
        ]
        
        calculation_menu.make_window(size = (1200, 775))
        while True:
            calculation_menu.read()
            if calculation_menu.event is None:
                break
            if 'Calc' in calculation_menu.event:
                # インスタンス生成
                wc = WeighingCalculator(materials=list(dict_materials.values()))

                # 過剰量を辞書まとめる．
                dict_excess = {material: float(calculation_menu.values['{}_excess'.format(material)]) / 100 for material in dict_materials.values()}
                
                # 生成重量を変数として得る．
                mg = float(calculation_menu.values['mg'])
                if 'ratio' in calculation_menu.event:
                    try:
                        dict_ratio = {}
                        for k, v in calculation_menu.values.items():
                            if k in dict_materials.values():
                                if v.count('/') > 1:
                                    raise ValueError
                                elif '/' in v:
                                    dict_ratio[k] = float(v.split('/')[0]) / float(v.split('/')[1])
                                else:
                                    dict_ratio[k] = float(v)
                    except ValueError:  # try内で指定したValueError以外も含めて．
                        sg.popup_error('You have not entered any. Or the value you entered is not good.\nCorrect: 1/3, 1, 1.0, 3.141 etc.', **self.option_text_default, modal = False, keep_on_top=True)
                        continue
                    wc.calc(ratio = list(dict_ratio.values()), mg = mg, excess = dict_excess, match_all = True, progress_bar = False)
                elif 'product' in calculation_menu.event:
                    if calculation_menu.values['product'] == '':
                        sg.popup_error('Nothing has been entered.', **self.option_text_default, modal = False, keep_on_top=True)
                        continue
                    try:    # match_all=Trueでうまくいかなかったとき
                        wc.calc(products=[calculation_menu.values['product']], mg = mg, excess = dict_excess, match_all = True, progress_bar = False)
                    except ValueError:
                        try:
                            wc.calc(products=[calculation_menu.values['product']], mg = mg, excess = dict_excess, match_all = False, progress_bar = False)
                        except ValueError:  # match_all=Falseでもうまくいかなかったとき
                            sg.PopupError('The composition you have entered is invalid.', **self.option_text_default, modal = False, keep_on_top=True)
                            continue
                        else:
                            sg.popup_ok('The results of the calculations may be different because they did not match exactly.', **self.option_text_default, modal = False, keep_on_top=True)

                self._table(wc = wc)
        
        calculation_menu.window.close()

    def _table(self, wc):
        '''
        wc: WeighingCalculatorオブジェクト
        '''
        # 出力用の表を作成
        df_output, df_output_show = self._make_output(wc)
        df_output_show.drop(index = ['measured value (mg)'], inplace = True)
        df_output.index.name = ''
        df_output_show.index.name = ''
        df_output_show.reset_index(inplace=True)

        # オブジェクトの生成
        table_menu = Menu(self)

        # layoutの作成
        table_menu.layout = [
            [sg.Table(df_output_show.to_numpy().tolist(), headings = df_output_show.columns.to_numpy().tolist(), col_widths = [16] + [10] * (df_output_show.shape[1]-2) + [16], auto_size_columns = False, hide_vertical_scroll=False)],
            [sg.Cancel(), sg.InputText(key='SaveAs', do_not_clear=False, enable_events=True, visible=False), sg.FileSaveAs('SaveAs', default_extension = '.xlsx', file_types = (('Excel file', '*.xlsx'),))],   # do_not_clearをFalseにしないとCancelしても上書きされてしまう．あと，sg.FilseSaveAsのenable_event = Trueにしてもenentが発生しないのでsg.InputTextで受け取るときにeventを発生させている．
        ]

        # windowの作成
        table_menu.make_window(size = (1200, 600))

        while True:
            table_menu.read()
            if table_menu.event in (None, 'Cancel'):
                pass
            elif table_menu.event == 'SaveAs':
                if table_menu.values['SaveAs'] == '':
                    continue
                df_output.reset_index().to_excel(table_menu.values['SaveAs'], index = False)
                sg.PopupOK('Saved successfully.', modal = True, **self.option_text_default)
            break
            
                
        table_menu.window.close()

    def _make_output(self, wc):
        '''
        wc: WeighingCalculatorオブジェクト
        '''
        cols = wc.materials + wc.products
        ind = ['M.W.', 'molar ratio', 'mole (mmol)', 'excess ratio (mol%)', 'mole w/ excess', 'no excess weight (mg)', 'weight (mg)', 'measured value (mg)']
        df_output = pd.DataFrame([[np.nan] * len(cols)] * len(ind), columns = cols, index = ind)

        # 式量を代入
        for material in wc.materials:
            df_output.loc['M.W.', material] = wc.dict_materials[material].weight
        df_output.loc['M.W.', wc.products[0]] = wc.dict_products[wc.products[0]].weight

        # モル比を代入
        df_output.loc['molar ratio', wc.df_ratio.columns] = wc.df_ratio.values
        df_output.loc['molar ratio', wc.products] = 1

        # モル数を代入
        df_output.loc['mole (mmol)'] = df_output.loc['molar ratio'] * wc.moles[0]

        # 過剰量
        for material, ex in wc.excess.items():
            df_output.loc['excess ratio (mol%)', material] = ex * 100

        # 過剰量込のモル数
        df_output.loc['mole w/ excess'] = df_output.loc['mole (mmol)'] * (1 + df_output.loc['excess ratio (mol%)'] / 100)
        for material in wc.materials:
            if np.isnan(df_output.loc['mole w/ excess', material]):
                df_output.loc['mole w/ excess', material] = df_output.loc['mole (mmol)', material]

        # 過剰量なしの重量
        df_output.loc['no excess weight (mg)', wc.df_material_weight.columns] = wc.df_material_weight.loc[wc.products[0]]
        df_output.loc['no excess weight (mg)', wc.products[0]] = df_output.loc['no excess weight (mg)', wc.df_material_weight.columns].sum()

        # 過剰量ありの重量
        df_output.loc['weight (mg)', wc.df_material_weight_excess.columns] = wc.df_material_weight_excess.loc[wc.products[0]]
        df_output.loc['weight (mg)', wc.products[0]] = df_output.loc['weight (mg)', wc.df_material_weight_excess.columns].sum()

        # 表示用のdf_outputを作成
        df_output_show = df_output.applymap(lambda x:'{:.2f}'.format(x))
        df_output_show.replace('nan', '', inplace=True)

        return df_output, df_output_show
        # print(wc.materials)
        # df_output = pd.DataFrame()


class Menu:
    def __init__(self, gui):
        self.gui = gui
        self.layout = [[]]

    def make_window(self, **options):
        default_options = {
            'size' : (800, 450),
            "font" : (self.gui.font_default, self.gui.font_size_default),
            'element_justification' : 'center',
            'resizable': True
        }
        default_options.update(**options)
        self.window = sg.Window(self.gui.APP_NAME, layout = self.layout, **default_options)

    def read(self):
        self.event, self.values = self.window.read()
    
            
if __name__ == '__main__':
    # from pdb import set_trace
    app = gui()
    app.run()