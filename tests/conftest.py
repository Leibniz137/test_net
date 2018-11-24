def pytest_addoption(parser):
    parser.addoption(
        '--secret-file',
        default='.secret',
        help="any passphrase that Geth will use to encrypt your private key")
