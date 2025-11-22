import pytest
from unittest.mock import patch
from schemas import BicycleDetect


if __name__ == "__main__":
    bicycle = BicycleDetect.getOne(1)
    print(bicycle)