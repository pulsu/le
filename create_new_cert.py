from helpers import params_main
from controller import CreateNewCert

if __name__ == '__main__':
    params = params_main()
    CreateNewCert(**params)
