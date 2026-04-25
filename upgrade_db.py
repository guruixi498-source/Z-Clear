import database
from sqlalchemy import text

def upgrade():
    print("正在执行数据库升级脚本...")
    with database.engine.connect() as conn:
        try:
            # 尝试 MariaDB Vector 语法
            print("尝试应用 MariaDB Vector 原生表结构...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_regulations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    content TEXT,
                    hs_code VARCHAR(50),
                    country VARCHAR(100),
                    embedding VECTOR(1536),
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX(hs_code),
                    INDEX(country)
                )
            """))
            conn.commit()
            print("MariaDB 表结构升级成功！")
        except Exception as e:
            # 降级到 SQLite
            print(f"MariaDB 语法执行失败，降级到 SQLite 结构 (原因: {e})")
            database.Base.metadata.create_all(bind=database.engine)
            print("SQLite 表结构升级成功！")

if __name__ == "__main__":
    upgrade()
