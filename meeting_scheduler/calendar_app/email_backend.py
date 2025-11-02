"""
Custom email backend that bypasses SSL certificate verification.

This is ONLY for development/testing purposes to work around Windows SSL certificate issues.
DO NOT use in production.
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend


class UnsecureEmailBackend(EmailBackend):
    """
    Custom email backend that disables SSL certificate verification.

    WARNING: This is insecure and should ONLY be used for development testing.
    """

    def open(self):
        """
        Open connection with disabled SSL verification.
        """
        if self.connection:
            return False

        connection_params = {}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl:
            # Create an SSL context that doesn't verify certificates
            connection_params['context'] = ssl._create_unverified_context()

        try:
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )

            if not self.use_ssl and self.use_tls:
                # Create an unverified context for STARTTLS
                self.connection.starttls(context=ssl._create_unverified_context())

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception:
            if not self.fail_silently:
                raise
