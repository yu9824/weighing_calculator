# Weighing Calculator
## What is this.
This is a package for performing weighing calculations, with GUI operation available only on OS X.

## How to build

```bash
conda create -yn wc python=3.9.6 -c conda-forge --file=requirements-conda.txt
conda activate wc
pip install -r requirements-pip.txt
```

If you would like to develop by using jupyter, you have to install jupyter like this;

```bash
conda install jupyter
```

## How to install
You can check the [Releases](https://github.com/yu9824/weighing_calculator/releases) and directly download the file in `.app` format for a specific version.


Alternatively, you can also clone the git repository and setup it on your own computer.

```bash
git clone https://github.com/yu9824/weighing_calculator.git
```

I think the former way is easier.


### How to setup GUI app when you clone this repository
Execute the following command in an environment where the package described in `requirements.txt` has been installed.

```bash
cd weighing_calculator
python3 setup.py py2app -A
```

## How to uninstall
You only need to delete `.app`. Namely, move the app to trash.

If you would like to update the app, please uninstall it at first and reinstall the newer version.


## How to use
![start menu](https://github.com/yu9824/weighing_calculator/blob/67b3611eaf948b65c13703f8539a0c9e99eaeb5a/example/img/start_menu.png)

![materials menu](https://github.com/yu9824/weighing_calculator/blob/67b3611eaf948b65c13703f8539a0c9e99eaeb5a/example/img/materials_menu.png)

![calculation menu](https://github.com/yu9824/weighing_calculator/blob/67b3611eaf948b65c13703f8539a0c9e99eaeb5a/example/img/calculation_menu.png)

![result window](https://github.com/yu9824/weighing_calculator/blob/67b3611eaf948b65c13703f8539a0c9e99eaeb5a/example/img/result_window.png)

## LICENSE
This software is released under the GNU LESSER GENERAL PUBLIC LICENSE Version 3, see [LICENSE](https://github.com/yu9824/weighing_calculator/blob/main/LICENSE).

Copyright © 2021,  yu9824


## Histories
### v0.5.0
Rename username.
Update python from python3.7 to python3.9.6
Delete xlwt from requirements (only openpyxl is enough.)
py2app=0.24 does not work correctly, thus I use py2app=0.23

Note: latest pymatgen has some error. (Import error occurred.) So we use pymatgen=2020.12.31

### v0.6.0
3.10.0はサポートしていると書かれているのものサポートされていないと考える方が妥当な結果．（ビルドに失敗する．）
Downgrade python to 3.8.10.
Montereyだとpython3.8でpysimpleguiのsaveasが動かない．
日本語と英語に対応．
前回入力した原料をキャッシュとして保持できる．