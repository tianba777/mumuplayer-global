# 发布到 PyPI

## 1. 准备账号和令牌

1. 在 https://pypi.org 注册并登录。
2. 在 `Account settings -> API tokens` 创建 token。
3. 首次建议先发布到 TestPyPI：https://test.pypi.org

## 2. 构建包

```powershell
python -m pip install -U build twine
python -m build
```

产物会在 `dist/` 下，包含 `.whl` 和 `.tar.gz`。

## 3. 检查包元数据

```powershell
python -m twine check dist/*
```

## 4. 上传到 TestPyPI（推荐先做）

```powershell
python -m twine upload --repository testpypi dist/*
```

安装验证：

```powershell
python -m pip install -i https://test.pypi.org/simple/ mumu-python-api-wlkjyy
```

## 5. 上传到正式 PyPI

```powershell
python -m twine upload dist/*
```

## 6. 可选：使用环境变量避免明文输入

```powershell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-xxxx"
python -m twine upload dist/*
```
