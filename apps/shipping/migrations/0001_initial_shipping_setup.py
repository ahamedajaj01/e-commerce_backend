import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Full replacement migration for the Shipping app.

    Drops the old multi-table schema (ShippingZone, ShippingRegion,
    ShippingMethod, ShippingRule) and replaces it with:
      - ShippingProvider  (kept for future courier API integrations)
      - ShippingRule      (new flat, hierarchical rule table)
    """

    initial = True

    dependencies = []

    operations = [
        # ── Drop old tables if they exist ─────────────────────────
        migrations.RunSQL(
            sql=[
                # Drop in FK-dependency order (children first)
                "DROP TABLE IF EXISTS shipping_shippingrule;",
                "DROP TABLE IF EXISTS shipping_shippingregion;",
                "DROP TABLE IF EXISTS shipping_shippingmethod;",
                "DROP TABLE IF EXISTS shipping_shippingzone;",
                "DROP TABLE IF EXISTS shipping_shippingprovider;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),

        # ── Create ShippingProvider ───────────────────────────────
        migrations.CreateModel(
            name='ShippingProvider',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('code', models.SlugField(unique=True)),
                ('provider_type', models.CharField(
                    choices=[('MANUAL', 'Manual/Internal'), ('API', 'External API')],
                    default='MANUAL', max_length=20
                )),
                ('is_active', models.BooleanField(default=True)),
                ('configuration', models.JSONField(blank=True, default=dict)),
            ],
            options={'abstract': False},
        ),

        # ── Create ShippingRule (new flat, hierarchical model) ─────
        migrations.CreateModel(
            name='ShippingRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=150, help_text="Human-readable label e.g. 'Kathmandu District'")),
                ('province', models.CharField(max_length=100, blank=True, default='')),
                ('district', models.CharField(max_length=100, blank=True, default='')),
                ('city_or_municipality', models.CharField(max_length=100, blank=True, default='')),
                ('shipping_fee', models.DecimalField(max_digits=10, decimal_places=2)),
                ('estimated_days', models.CharField(max_length=50, blank=True, default='3-5 Business Days')),
                ('priority', models.PositiveIntegerField(
                    default=10,
                    help_text='Lower number = higher priority. Auto-set based on geo-specificity.'
                )),
                ('is_default', models.BooleanField(
                    default=False,
                    help_text='If True, this rule applies to any address with no other match. Only one default allowed.'
                )),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['priority', 'province', 'district', 'city_or_municipality']},
        ),
    ]
