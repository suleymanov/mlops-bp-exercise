FROM public.ecr.aws/lambda/python:3.11

RUN pip install -U pip
RUN pip install numpy==2.2.6 scipy==1.15.3 scikit-learn==1.6.1 "botocore[crt]"

COPY [ "lambda_function.py", "model.py", "./" ]
# COPY [ "lin_reg.bin", "./"]

CMD [ "lambda_function.lambda_handler" ]
