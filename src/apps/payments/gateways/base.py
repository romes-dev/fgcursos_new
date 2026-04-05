from abc import ABC, abstractmethod


class BaseGateway(ABC):
    """Interface base para gateways de pagamento."""

    @abstractmethod
    def create_preference(self, order):
        """
        Cria uma preferência de pagamento no gateway.
        Retorna dict com: {'preference_id': ..., 'init_point': ...}
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment(self, payment_id):
        """
        Consulta o status de um pagamento no gateway.
        Retorna dict com: {'id': ..., 'status': ..., 'payment_method_id': ..., 'raw': ...}
        """
        raise NotImplementedError

    def normalize_status(self, gateway_status):
        """Normaliza o status do gateway para o status interno."""
        return gateway_status
