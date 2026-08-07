import uuid
from django.conf import settings
from django.db import models


class NailServiceType(models.TextChoices):
    ESCULPIDAS = 'esculpidas', 'Esculpidas'
    SEMIPERMANENTE = 'semipermanente', 'Semipermanente'
    KAPPING = 'kapping', 'Kapping'
    SOFT_GEL = 'soft_gel', 'Soft gel'
    RETOQUE = 'retoque', 'Retoque'
    RETIRADA = 'retirada', 'Retirada'
    PIES = 'pies', 'Pies'
    OTRO = 'otro', 'Otro'


class ClothingStatus(models.TextChoices):
    IN_STOCK = 'in_stock', 'En stock'
    SOLD = 'sold', 'Vendido'
    RESERVED = 'reserved', 'Reservado'
    RETURNED = 'returned', 'Devuelto'


class NailService(models.Model):
    """Servicio de uñas realizado. Montos en ARS."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nail_services',
        verbose_name='Usuario'
    )
    client_name = models.CharField('Cliente', max_length=200)
    service_type = models.CharField(
        'Tipo de servicio',
        max_length=20,
        choices=NailServiceType.choices
    )
    price = models.DecimalField('Precio', max_digits=12, decimal_places=2)
    cost = models.DecimalField('Costo de insumos', max_digits=12, decimal_places=2, default=0)
    date = models.DateField('Fecha')
    notes = models.TextField('Notas', blank=True, default='')
    photo = models.ImageField('Foto', upload_to='araceli/nails/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Servicio de uñas'
        verbose_name_plural = 'Servicios de uñas'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.get_service_type_display()} ({self.date})"


class ClothingItem(models.Model):
    """Prenda comprada para reventa. Montos en ARS."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clothing_items',
        verbose_name='Usuario'
    )
    name = models.CharField('Nombre', max_length=200)
    category = models.CharField('Categoría', max_length=100, blank=True, default='')
    size = models.CharField('Talle', max_length=50, blank=True, default='')
    purchase_price = models.DecimalField('Precio de compra', max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(
        'Precio de venta', max_digits=12, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=ClothingStatus.choices,
        default=ClothingStatus.IN_STOCK
    )
    purchase_date = models.DateField('Fecha de compra')
    sale_date = models.DateField('Fecha de venta', null=True, blank=True)
    buyer_name = models.CharField('Comprador', max_length=200, blank=True, default='')
    notes = models.TextField('Notas', blank=True, default='')
    photo = models.ImageField('Foto', upload_to='araceli/clothing/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Prenda'
        verbose_name_plural = 'Prendas'
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
