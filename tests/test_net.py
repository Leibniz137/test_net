import re
import shlex
from subprocess import (
    run,
    PIPE,
)

import pytest


class Wallet:
    def __init__(self, private_key, public_key, address):
        self.skey = private_key
        self.pkey = public_key
        self.address = address

    @staticmethod
    def parse_skey(standard_out):
        m = re.search(r'(?<=Private key: )\w+', standard_out)
        if not m:
            raise ValueError
        skey = m.group(0)
        assert skey
        return skey

    @staticmethod
    def parse_pkey(standard_out):
        m = re.search(r'(?<=Public key:\s{2})\w+', standard_out)
        if not m:
            raise ValueError
        pkey = m.group(0)
        assert pkey
        return pkey

    @staticmethod
    def parse_addr(standard_out):
        m = re.search(r'(?<=Address:\s{5})\w+', standard_out)
        if not m:
            raise ValueError
        addr = m.group(0)
        assert addr
        return addr


@pytest.fixture
def wallet():
    create_wallet_cmd = shlex.split('python ethereum-generate-wallet/ethereum-wallet-generator.py')
    proc = run(
        create_wallet_cmd,
        encoding='utf-8',
        stdout=PIPE,
        stderr=PIPE,
        check=True)
    content = proc.stdout
    private_key = Wallet.parse_skey(content)
    public_key = Wallet.parse_pkey(content)
    address = Wallet.parse_addr(content)
    yield Wallet(private_key, public_key, address)


@pytest.fixture
def testnet(wallet):
    yield


def test_ing(testnet):
    pass
