import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


ssm = boto3.client('ssm', region_name='ap-northeast-2')


def get_parameter(name, with_decryption=True):
    """AWS Parameter Store에서 값을 가져오는 함수"""
    return ssm.get_parameter(Name=name, WithDecryption=with_decryption)['Parameter']['Value']

DATABASE_URL = f"mysql+pymysql://{get_parameter('/interviewdb-info/DB_USER')}:{get_parameter('/interviewdb-info/DB_PASSWORD', with_decryption=True)}@{get_parameter('/interviewdb-info/DB_HOST')}:{get_parameter('/interviewdb-info/DB_PORT')}/{get_parameter('/interviewdb-info/DB_NAME')}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)