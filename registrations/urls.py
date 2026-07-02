from django.urls import path
from .views import MyRegistrationsListView

# Define a rota de consumo das inscrições do usuário logado
urlpatterns = [
    # Endpoint ideal para popular a view de "Meus Eventos" ou "Dashboard" na interface em React
    path("me/", MyRegistrationsListView.as_view(), name="my-registrations"),
]