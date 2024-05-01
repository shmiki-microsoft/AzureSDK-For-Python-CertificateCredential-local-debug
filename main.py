import os
import logging
import sys
from azure.core import exceptions
from azure.identity import CertificateCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

#ロガーを取得
# azure. で始まるモジュールのログすべてを取得
logger = logging.getLogger('azure') 
# blob ストレージのログのみに絞るとき
# logger = logging.getLogger("azure.storage.blob")
# DefaultAzureCredentialのログのみに絞るとき
# logger = logging.getLogger('azure.identity')
#ログレベルを設定
logger.setLevel(logging.DEBUG)
# ログメッセージのフォーマットを設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ログメッセージをコンソールに出力するハンドラーを作成
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
# ロガーにハンドラーを追加
logger.addHandler(handler)

# ログレベルの確認
print(
    f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, "
    f"WARNING={logger.isEnabledFor(logging.WARNING)}, "
    f"INFO={logger.isEnabledFor(logging.INFO)}, "
    f"DEBUG={logger.isEnabledFor(logging.DEBUG)}"
)

try:
    #環境変数の設定内容の確認
    print("---環境変数の設定内容---")
    print("AZURE_CLIENT_ID",os.getenv("AZURE_CLIENT_ID"))
    print("AZURE_CLIENT_SECRET",os.getenv("AZURE_CLIENT_SECRET"))
    print("AZURE_TENANT_ID",os.getenv("AZURE_TENANT_ID"))
    print("AZURE_CLIENT_CERTIFICATE_PATH",os.getenv("AZURE_CLIENT_CERTIFICATE_PATH"))
    print("AZURE_CLIENT_CERTIFICATE_PASSWORD",os.getenv("AZURE_CLIENT_CERTIFICATE_PASSWORD"))
    print("AZURE_USERNAME",os.getenv("AZURE_USERNAME"))
    print("AZURE_PASSWORD",os.getenv("AZURE_PASSWORD"))
    print("-----------------------")

    # 認証オブジェクトを取得
    # logging_enable=True で HTTTP のログも出力デバックログを出力
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    cert_path = os.getenv("AZURE_CLIENT_CERTIFICATE_PATH")
    cert_password = os.getenv("AZURE_CLIENT_CERTIFICATE_PASSWORD")
    #証明書が .pfx ファイルの時
    token_credential = CertificateCredential(
        tenant_id=tenant_id,
        client_id=client_id, 
        certificate_path=cert_path,
        password=cert_password, 
        logging_enable=True)

    # 証明書が .pem ファイルの時
    # token_credential = CertificateCredential(
    #     tenant_id=tenant_id,
    #     client_id=client_id, 
    #     certificate_path=cert_path,
    #     logging_enable=True)

    # 取得するトークンのチェック
    # 明示的にトークンを取得 実行しなくてもblob_service_client.list_containers() など
    # 各 Azure リソース側のメソッドが自動的にトークンを呼び出し取得してくれる
    access_token_raw = token_credential.get_token("https://management.azure.com//.default").token
    print("access_token_raw",access_token_raw)

    # BlobServiceClient オブジェクトを作成
    #logging_enable=Trueでデバックログも  logging_body=True で HTTP のログも出力
    blob_service_client = BlobServiceClient(
        account_url=os.getenv("blob_service_uri"),
        credential=token_credential,
        logging_body=True,
        logging_enable=True)
    # 全てのコンテナをリストし、それらをコンソールに出力
    container_list = blob_service_client.list_containers()
    #print("\nList of containers in the storage account:")
    for container in container_list:
        print(container.name)

except (
    exceptions.ClientAuthenticationError,
    exceptions.HttpResponseError
) as e:
    print(e.message)