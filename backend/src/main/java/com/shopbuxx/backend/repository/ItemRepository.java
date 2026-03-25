package com.shopbuxx.backend.repository;

import com.shopbuxx.backend.model.Item;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ItemRepository extends MongoRepository<Item, String> {
    List<Item> findByRarity(String rarity);
}
