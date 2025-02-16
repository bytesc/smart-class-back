import sqlalchemy
import uvicorn
from fastapi import FastAPI
from utils.get_config import config_data


DATABASE_URL = config_data['mysql']
engine = sqlalchemy.create_engine(DATABASE_URL)



app = FastAPI()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
