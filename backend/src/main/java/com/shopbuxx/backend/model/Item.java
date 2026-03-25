package com.shopbuxx.backend.model;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.math.BigDecimal;

@Data
@Document(collection = "items")
public class Item {
    @Id
    private String id;
    private String name;
    private String description;
    private String rarity;
    private BigDecimal price;
    private int stock;
    private String imageUrl;
}
