FROM public.ecr.aws/lambda/python:3.12

COPY pyproject.toml ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda/ ${LAMBDA_TASK_ROOT}/lambda/

RUN pip install --no-cache-dir . --target "${LAMBDA_TASK_ROOT}"

CMD ["lambda.handler.lambda_handler"]