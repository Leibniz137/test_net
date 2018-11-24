import re
import shlex
from subprocess import (
    run,
    PIPE,
)

import pytest


def parser(regex):
    def decorator(func):
        def parse_item(standard_out):
            m = re.search(regex, standard_out)
            if not m:
                raise ValueError
            item = m.group(0)
            assert item
            return item
        return parse_item
    return decorator


class Wallet:
    def __init__(self, private_key, public_key, address):
        self.skey = private_key
        self.pkey = public_key
        self.addr = address

    @staticmethod
    @parser(r'(?<=Private key: )\w+')
    def parse_skey():
        pass

    @staticmethod
    @parser(r'(?<=Public key:\s{2})\w+')
    def parse_pkey():
        pass

    @staticmethod
    @parser(r'(?<=Address:\s{5})\w+')
    def parse_addr():
        pass


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def secret(request):
    path = request.config.getoption('--secret-file')
    if not path:
        raise ValueError("secret required to initialize testnet: use --secret-file")
    with open(path) as fp:
        text = fp.read().strip()
    yield text


@pytest.fixture(scope="session")
def testnet(wallet, secret):
    release = 'test-net'
    cmdstr = (
        "helm install --name {release}"
        " --set geth.account.address='{address}'"
        " --set geth.account.privateKey='{private_key}'"
        " --set geth.account.secret='{secret}'"
        " charts/stable/ethereum"
    ).format(
        release=release,
        secret=secret,
        address=wallet.addr,
        private_key=wallet.pkey,
    )
    helm_install_cmd = shlex.split(cmdstr)
    run(helm_install_cmd, check=True)
    yield
    helm_delete_cmd = shlex.split(f'helm delete {release}')
    run(helm_delete_cmd)


def test_ing(testnet):
    pass
