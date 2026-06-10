"""
Image Serving and API Documentation

Fix for 404 Error: http://localhost:8000/api/v1/media/products/media/sarees1.webp

ISSUE:
The frontend was requesting images from /api/v1/media/ which doesn't exist.
Django serves media files from /media/ directly, not through the API.

SOLUTION:
Images are now included in API responses with proper URLs.
Frontend should use the file_url field from the product API response.

================================================================================
API ENDPOINTS
================================================================================

1. GET /api/v1/storefront/products
   
   Description: Get all products with images
   
   Response:
   {
       "data": [
           {
               "id": 1,
               "name": "Sarees",
               "slug": "sarees",
               "description": "Beautiful sarees",
               "category": "Clothing",
               "variants": [...],
               "media": [
                   {
                       "id": 1,
                       "media_type": "IMAGE",
                       "file": "products/media/sarees1.webp",
                       "file_url": "/media/products/media/sarees1.webp",  ← USE THIS!
                       "alt_text": "Saree image",
                       "sort_order": 0
                   }
               ]
           }
       ]
   }

2. GET /api/v1/storefront/categories
   
   Description: Get all categories

3. GET /api/v1/products/{id}/
   
   Description: Get single product with full details (if using the new ProductViewSet)

4. GET /api/v1/products/{id}/images/
   
   Description: Get only images for a product (if using the new ProductViewSet)

================================================================================
HOW TO DISPLAY IMAGES IN FRONTEND
================================================================================

WRONG (404 Error):
   <img src="/api/v1/media/products/media/sarees1.webp" />
   
   ❌ This path doesn't exist and returns 404

CORRECT:
   // Get products from API
   const response = await fetch('/api/v1/storefront/products');
   const { data } = await response.json();
   
   // Use file_url from the API response
   data.forEach(product => {
       product.media.forEach(media => {
           const imageUrl = media.file_url;  // e.g., "/media/products/media/sarees1.webp"
           console.log(imageUrl);
           
           // Use in your HTML
           const img = document.createElement('img');
           img.src = imageUrl;
           img.alt = media.alt_text;
           container.appendChild(img);
       });
   });

   ✅ This works! Images are served from /media/ which is configured in Django

ABSOLUTE URLS:
   If your frontend is on a different domain, the API will return absolute URLs:
   
   {
       "file_url": "http://localhost:8000/media/products/media/sarees1.webp"
   }

================================================================================
REACT EXAMPLE
================================================================================

import React, { useState, useEffect } from 'react';

function ProductGallery() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/v1/storefront/products')
            .then(res => res.json())
            .then(data => {
                setProducts(data.data);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error loading products:', err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div className="product-gallery">
            {products.map(product => (
                <div key={product.id} className="product-card">
                    <h3>{product.name}</h3>
                    <div className="product-images">
                        {product.media.map(media => (
                            // Use file_url instead of file!
                            <img
                                key={media.id}
                                src={media.file_url}  // ← This is the key!
                                alt={media.alt_text}
                                className="product-image"
                            />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ProductGallery;

================================================================================
VUE.JS EXAMPLE
================================================================================

<template>
    <div class="product-gallery">
        <div v-for="product in products" :key="product.id" class="product-card">
            <h3>{{ product.name }}</h3>
            <div class="product-images">
                <img
                    v-for="media in product.media"
                    :key="media.id"
                    :src="media.file_url"  <!-- Use file_url -->
                    :alt="media.alt_text"
                    class="product-image"
                />
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ProductGallery',
    data() {
        return {
            products: [],
            loading: true
        };
    },
    mounted() {
        fetch('/api/v1/storefront/products')
            .then(res => res.json())
            .then(data => {
                this.products = data.data;
                this.loading = false;
            })
            .catch(err => {
                console.error('Error loading products:', err);
                this.loading = false;
            });
    }
};
</script>

================================================================================
ANGULAR EXAMPLE
================================================================================

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-product-gallery',
    template: `
        <div class="product-gallery">
            <div *ngFor="let product of products" class="product-card">
                <h3>{{ product.name }}</h3>
                <div class="product-images">
                    <img
                        *ngFor="let media of product.media"
                        [src]="media.file_url"  <!-- Use file_url -->
                        [alt]="media.alt_text"
                        class="product-image"
                    />
                </div>
            </div>
        </div>
    `
})
export class ProductGalleryComponent implements OnInit {
    products = [];
    loading = true;

    constructor(private http: HttpClient) {}

    ngOnInit() {
        this.http.get('/api/v1/storefront/products')
            .subscribe((data: any) => {
                this.products = data.data;
                this.loading = false;
            });
    }
}

================================================================================
COMMON ISSUES AND SOLUTIONS
================================================================================

1. Still getting 404 errors?
   
   Issue: Frontend is still using /api/v1/media/ or /file field
   Solution: Use file_url field from API response instead
   
   Example:
   ✅ CORRECT:  <img src={media.file_url} />
   ❌ WRONG:    <img src={"/api/v1/media/" + media.file} />

2. Images not showing in development?
   
   Causes:
   - Django DEBUG=False (disabled media serving)
   - Media files don't exist
   - Permissions issues
   
   Solutions:
   - Ensure DEBUG=True in development (.env)
   - Verify files exist in media/products/media/
   - Check file permissions: ls -la media/

3. Relative vs Absolute URLs?
   
   Relative URL (development):
   /media/products/media/sarees1.webp
   
   Absolute URL (production with CORS):
   http://localhost:8000/media/products/media/sarees1.webp
   OR
   https://yourdomain.com/media/products/media/sarees1.webp
   
   The API automatically detects which to return based on request context.

4. CORS issues with media files?
   
   In production, configure CORS for media domain:
   
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:3000',
       'https://yourdomain.com',
   ]
   
   And make sure your web server (nginx) serves media with proper CORS headers.

================================================================================
FILE STRUCTURE
================================================================================

Backend structure:
/media/
├── products/
│   ├── media/
│   │   ├── sarees1.webp        ← Uploaded files go here
│   │   ├── sarees2.webp
│   │   └── ...
│   └── ...
└── ...

URL mapping:
File: media/products/media/sarees1.webp
URL:  /media/products/media/sarees1.webp (relative)
      http://localhost:8000/media/products/media/sarees1.webp (absolute)

API response field: media.file_url = "/media/products/media/sarees1.webp"

================================================================================
PRODUCTION SETUP
================================================================================

For production, images should be served by a reverse proxy (nginx) or CDN:

1. Nginx Configuration:
   
   location /media/ {
       alias /var/www/allinonenepal/media/;
       expires 30d;
       add_header Cache-Control "public, immutable";
   }

2. CDN Setup (Recommended):
   
   - Upload media files to AWS S3, GCS, or similar
   - Update Django settings to use S3 backend
   - Return CDN URLs in API responses

3. Django S3 Setup:
   
   INSTALLED_APPS += ['storages']
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   AWS_S3_REGION_NAME = 'us-east-1'
   AWS_STORAGE_BUCKET_NAME = 'your-bucket'

================================================================================
TESTING
================================================================================

Test the image endpoints:

1. Get all products with images:
   
   curl http://localhost:8000/api/v1/storefront/products

2. Verify file_url field exists:
   
   curl http://localhost:8000/api/v1/storefront/products | jq '.data[0].media[0].file_url'

3. Verify image can be accessed:
   
   curl -I http://localhost:8000/media/products/media/sarees1.webp
   (Should return HTTP 200, not 404)

================================================================================
SUMMARY
================================================================================

OLD (❌ WRONG):
POST /api/v1/media/products/media/sarees1.webp → 404

NEW (✅ CORRECT):
1. GET /api/v1/storefront/products → Returns products with file_url
2. frontend uses file_url like: /media/products/media/sarees1.webp
3. Django serves from /media/ directory

Key takeaway:
✅ Use file_url field from API response
❌ Don't use file field directly
❌ Don't prepend /api/v1/media/
"""
