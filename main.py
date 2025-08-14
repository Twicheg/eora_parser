import config
import uvicorn
import pytest

config.configure_logging()

if __name__ == "__main__":
    pytest.main()
    uvicorn.run(app_dir="web_api", app="app:app",host=config.HOST, port=int(config.PORT), reload=True)