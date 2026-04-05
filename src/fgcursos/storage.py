from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    # Prefixo "fgcursos/media" isola os arquivos dentro do bucket compartilhado
    location = 'fgcursos/media'
    file_overwrite = False
    default_acl = None  # R2 não suporta ACLs
