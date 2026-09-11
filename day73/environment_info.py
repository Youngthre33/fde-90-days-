import sys

import fastapi
import uvicorn


print(
    "当前解释器：",
    sys.executable
)

print(
    "Python 版本：",
    sys.version
)

print(
    "FastAPI 版本：",
    fastapi.__version__
)

print(
    "FastAPI 位置：",
    fastapi.__file__
)

print(
    "Uvicorn 版本：",
    uvicorn.__version__
)
