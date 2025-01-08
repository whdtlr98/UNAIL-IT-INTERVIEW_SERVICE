from fastapi import APIRouter, HTTPException, Depends, Request
import boto3



ssm_client = boto3.client('ssm', region_name='ap-northeast-2')  # 서울 리전

def get_parameter(parameter_name):
    try:
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parameter: {str(e)}")