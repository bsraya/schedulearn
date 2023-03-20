from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["sha256_crypt", "ldap_salted_md5"],
    sha256_crypt__default_rounds=91234,
    ldap_salted_md5__salt_size=16,
    deprecated="auto"
)