"""
Global file cleanup signals.
Automatically deletes physical media files from disk whenever a model
instance that owns a FileField or ImageField is deleted. This keeps the
media/ folder in sync with the database so no orphan files accumulate.
"""
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db import models


def _delete_file(path: str):
    """Remove a file from disk if it actually exists."""
    if path:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass  # silently ignore permission or race-condition errors


def _get_file_fields(instance):
    """Yield the current file path for every FileField / ImageField on the instance."""
    for field in instance._meta.get_fields():
        if isinstance(field, (models.FileField,)):
            file_field = getattr(instance, field.name, None)
            if file_field and file_field.name:
                yield file_field.path


# ── Catalog ──────────────────────────────────────────────────────────────────

@receiver(post_delete, sender='catalog.ProductMedia')
def delete_product_media_file(sender, instance, **kwargs):
    _delete_file(instance.file.path if instance.file else None)


@receiver(pre_save, sender='catalog.ProductMedia')
def replace_product_media_file(sender, instance, **kwargs):
    """Delete old file when a media record's file is swapped for a new one."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.file and old.file != instance.file:
        _delete_file(old.file.path)


# ── CMS: Banner ───────────────────────────────────────────────────────────────

@receiver(post_delete, sender='cms.Banner')
def delete_banner_file(sender, instance, **kwargs):
    _delete_file(instance.image.path if instance.image else None)


@receiver(pre_save, sender='cms.Banner')
def replace_banner_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        _delete_file(old.image.path)


# ── CMS: Promotion ────────────────────────────────────────────────────────────

@receiver(post_delete, sender='cms.Promotion')
def delete_promotion_file(sender, instance, **kwargs):
    _delete_file(instance.image.path if instance.image else None)


@receiver(pre_save, sender='cms.Promotion')
def replace_promotion_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        _delete_file(old.image.path)
