
export VIRTUALENV_NAMESPACE='pymna-env'
export LOGURU_LEVEL="DEBUG"
export VIRTUALENV_PATH=$PWD/$VIRTUALENV_NAMESPACE


if [ -d "$VIRTUALENV_PATH" ]; then
    echo "$VIRTUALENV_PATH exists."
    source $VIRTUALENV_PATH/bin/activate
    export PYTHONPATH=$PYTHONPATH:$PWD

else
    virtualenv -p python ${VIRTUALENV_PATH}
    source $VIRTUALENV_PATH/bin/activate
    pip install -e .
    export PYTHONPATH=$PYTHONPATH:$PWD
fi