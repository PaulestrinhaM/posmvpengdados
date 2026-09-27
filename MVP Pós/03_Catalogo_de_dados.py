# Databricks notebook source
# DBTITLE 1,Organização do Unity Catalog - Projeto Pós-MVP
# MAGIC %md
# MAGIC # Organização do Unity Catalog - Projeto Pós-MVP
# MAGIC
# MAGIC Este notebook documenta toda a organização do catálogo `pospucrio` no Unity Catalog da Databricks.
# MAGIC
# MAGIC ## Arquitetura Medalhão
# MAGIC
# MAGIC | Camada | Schema | Descrição | Nomenclatura |
# MAGIC | --- | --- | --- | --- |
# MAGIC | Bronze | `pospucrio.bronze` | Dados brutos extraídos do Kaggle (9 CSVs Olist) | Original (inglês) |
# MAGIC | Silver | `pospucrio.silver` | Dados limpos e normalizados | Original (inglês) |
# MAGIC | Gold | `pospucrio.gold` | Tabelas analíticas prontas para negócio | Português |
# MAGIC

# COMMAND ----------

# DBTITLE 1,2. Comentários no catálogo, schemas e volume
# MAGIC %sql
# MAGIC -- ============================================
# MAGIC -- 2. COMENTÁRIOS NO CATÁLOGO, SCHEMAS E VOLUME
# MAGIC -- ============================================
# MAGIC
# MAGIC -- Catálogo
# MAGIC COMMENT ON CATALOG pospucrio IS 'Catálogo do projeto Pós-MVP: e-commerce Olist. Arquitetura Medallion (Bronze → Silver → Gold). Dados extraídos do Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC
# MAGIC -- Schemas
# MAGIC COMMENT ON SCHEMA pospucrio.bronze IS 'Camada Bronze: dados brutos extraídos do Kaggle (dataset Brazilian E-Commerce da Olist). Armazena os 9 CSVs originais em formato Delta, sem transformações.';
# MAGIC COMMENT ON SCHEMA pospucrio.silver IS 'Camada Silver: dados limpos e normalizados a partir da Bronze. Remove duplicatas, padroniza tipos e corrige typos do dataset original.';
# MAGIC COMMENT ON SCHEMA pospucrio.gold IS 'Camada Gold: tabelas analíticas prontas para consumo de negócio. Nomenclatura em português. Origem: tabelas Silver.';
# MAGIC
# MAGIC -- Volume
# MAGIC COMMENT ON VOLUME pospucrio.bronze.raw IS 'Volume de armazenamento dos 9 arquivos CSV originais da Olist, extraídos do Kaggle. Mantém os dados em formato bruto para auditoria e reprocessamento.';

# COMMAND ----------

# DBTITLE 1,3. Comentários nas tabelas Bronze
# MAGIC %sql
# MAGIC -- ============================================
# MAGIC -- 3. COMENTÁRIOS NAS TABELAS BRONZE
# MAGIC -- ============================================
# MAGIC
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_customers_dataset IS 'Dados brutos de clientes da Olist extraídos do Kaggle. Cada linha é um cliente único identificado por customer_id. Inclui CEP, cidade e estado. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_geolocation_dataset IS 'Dados brutos de geolocalização da Olist extraídos do Kaggle. Mapeia CEPs para coordenadas (latitude/longitude), cidade e estado. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_order_items_dataset IS 'Dados brutos de itens por pedido da Olist extraídos do Kaggle. Cada linha é um item de um pedido, com preço e frete. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_order_payments_dataset IS 'Dados brutos de pagamentos por pedido da Olist extraídos do Kaggle. Cada linha é um pagamento, podendo haver múltiplos por pedido. Inclui tipo, parcelas e valor. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_order_reviews_dataset IS 'Dados brutos de avaliações de pedidos da Olist extraídos do Kaggle. Cada linha é uma avaliação com nota de 1 a 5, título e comentário. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_orders_dataset IS 'Dados brutos de pedidos da Olist extraídos do Kaggle. Cada linha é um pedido com status, timestamps de compra, aprovação, envio e entrega. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_products_dataset IS 'Dados brutos de produtos da Olist extraídos do Kaggle. Cada linha é um produto com categoria, dimensões e peso. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.olist_sellers_dataset IS 'Dados brutos de vendedores da Olist extraídos do Kaggle. Cada linha é um vendedor com CEP, cidade e estado. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC COMMENT ON TABLE pospucrio.bronze.product_category_name_translation IS 'Tabela de tradução de nomes de categorias de produtos da Olist. Mapeia nome em português para inglês. Origem: Kaggle (olistbr/brazilian-ecommerce).';
# MAGIC
# MAGIC -- Colunas Bronze
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset ALTER COLUMN customer_id COMMENT 'Identificador único do cliente. Hash de 32 caracteres.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset ALTER COLUMN customer_unique_id COMMENT 'Identificador do cliente (não único por pedido). Mesmo cliente em pedidos diferentes tem o mesmo customer_unique_id.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset ALTER COLUMN customer_zip_code_prefix COMMENT 'Primeiros 5 dígitos do CEP do cliente.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset ALTER COLUMN customer_city COMMENT 'Cidade do endereço do cliente.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset ALTER COLUMN customer_state COMMENT 'UF (sigla do estado) do endereço do cliente.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_id COMMENT 'Identificador único do pedido.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN customer_id COMMENT 'Chave estrangeira para o cliente que fez o pedido.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_status COMMENT 'Status do pedido: delivered, shipped, canceled, unavailable, invoiced, processing, created ou approved.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_purchase_timestamp COMMENT 'Data e hora da compra pelo cliente.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_approved_at COMMENT 'Data e hora da aprovação do pagamento.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_delivered_carrier_date COMMENT 'Data e hora em que o pedido foi entregue à transportadora.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_delivered_customer_date COMMENT 'Data e hora da entrega ao cliente.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset ALTER COLUMN order_estimated_delivery_date COMMENT 'Data estimada de entrega informada ao cliente na compra.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN order_id COMMENT 'Chave estrangeira para o pedido.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN order_item_id COMMENT 'Número sequencial do item dentro do pedido, a partir de 1.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN product_id COMMENT 'Chave estrangeira para o produto.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN seller_id COMMENT 'Chave estrangeira para o vendedor.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN shipping_limit_date COMMENT 'Data limite para o vendedor despachar o item.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN price COMMENT 'Preço do item em reais.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset ALTER COLUMN freight_value COMMENT 'Valor do frete do item em reais.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset ALTER COLUMN order_id COMMENT 'Chave estrangeira para o pedido.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset ALTER COLUMN payment_sequential COMMENT 'Sequencial do pagamento dentro do pedido (múltiplos pagamentos possíveis).';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset ALTER COLUMN payment_type COMMENT 'Tipo de pagamento: credit_card, boleto, voucher, debit_card ou not_defined.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset ALTER COLUMN payment_installments COMMENT 'Número de parcelas do pagamento.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset ALTER COLUMN payment_value COMMENT 'Valor do pagamento em reais.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_id COMMENT 'Identificador único da avaliação.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN order_id COMMENT 'Chave estrangeira para o pedido avaliado.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_score COMMENT 'Nota da avaliação, de 1 (pior) a 5 (melhor).';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_comment_title COMMENT 'Título do comentário da avaliação. Pode ser nulo.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_comment_message COMMENT 'Texto do comentário da avaliação. Pode ser nulo.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_creation_date COMMENT 'Data de criação da avaliação.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset ALTER COLUMN review_answer_timestamp COMMENT 'Data e hora da resposta à avaliação.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_id COMMENT 'Identificador único do produto.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_category_name COMMENT 'Nome da categoria do produto em português.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_name_lenght COMMENT 'Comprimento do nome do produto em caracteres.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_description_lenght COMMENT 'Comprimento da descrição do produto em caracteres.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_photos_qty COMMENT 'Quantidade de fotos do produto.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_weight_g COMMENT 'Peso do produto em gramas.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_length_cm COMMENT 'Comprimento do produto em centímetros.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_height_cm COMMENT 'Altura do produto em centímetros.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset ALTER COLUMN product_width_cm COMMENT 'Largura do produto em centímetros.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_sellers_dataset ALTER COLUMN seller_id COMMENT 'Identificador único do vendedor.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_sellers_dataset ALTER COLUMN seller_zip_code_prefix COMMENT 'Primeiros 5 dígitos do CEP do vendedor.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_sellers_dataset ALTER COLUMN seller_city COMMENT 'Cidade do vendedor.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_sellers_dataset ALTER COLUMN seller_state COMMENT 'UF (sigla do estado) do vendedor.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset ALTER COLUMN geolocation_zip_code_prefix COMMENT 'Primeiros 5 dígitos do CEP.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset ALTER COLUMN geolocation_lat COMMENT 'Latitude da localização.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset ALTER COLUMN geolocation_lng COMMENT 'Longitude da localização.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset ALTER COLUMN geolocation_city COMMENT 'Cidade da localização.';
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset ALTER COLUMN geolocation_state COMMENT 'UF (sigla do estado) da localização.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.bronze.product_category_name_translation ALTER COLUMN product_category_name COMMENT 'Nome da categoria em português.';
# MAGIC ALTER TABLE pospucrio.bronze.product_category_name_translation ALTER COLUMN product_category_name_english COMMENT 'Nome da categoria em inglês.';

# COMMAND ----------

# DBTITLE 1,4. Comentários nas tabelas Silver
# MAGIC %sql
# MAGIC -- ============================================
# MAGIC -- 4. COMENTÁRIOS NAS TABELAS SILVER
# MAGIC -- ============================================
# MAGIC
# MAGIC COMMENT ON TABLE pospucrio.silver.customers IS 'Tabela de clientes limpa e normalizada a partir de bronze.olist_customers_dataset. Remove duplicatas e padroniza formatos de CEP, cidade e estado.';
# MAGIC COMMENT ON TABLE pospucrio.silver.order_items IS 'Tabela de itens por pedido limpa e normalizada a partir de bronze.olist_order_items_dataset. Padroniza tipos de preço e frete.';
# MAGIC COMMENT ON TABLE pospucrio.silver.order_payments IS 'Tabela de pagamentos por pedido limpa e normalizada a partir de bronze.olist_order_payments_dataset. Padroniza tipos de pagamento e valores.';
# MAGIC COMMENT ON TABLE pospucrio.silver.order_reviews IS 'Tabela de avaliações limpa e normalizada a partir de bronze.olist_order_reviews_dataset. Padroniza notas e timestamps.';
# MAGIC COMMENT ON TABLE pospucrio.silver.orders IS 'Tabela de pedidos limpa e normalizada a partir de bronze.olist_orders_dataset. Padroniza timestamps e status.';
# MAGIC COMMENT ON TABLE pospucrio.silver.products IS 'Tabela de produtos limpa e normalizada a partir de bronze.olist_products_dataset. Padroniza categorias e dimensões. Inclui nome de categoria em português.';
# MAGIC COMMENT ON TABLE pospucrio.silver.sellers IS 'Tabela de vendedores limpa e normalizada a partir de bronze.olist_sellers_dataset. Padroniza CEP, cidade e estado.';
# MAGIC
# MAGIC -- Colunas Silver - customers
# MAGIC ALTER TABLE pospucrio.silver.customers ALTER COLUMN customer_id COMMENT 'Identificador único do cliente (chave primária).';
# MAGIC ALTER TABLE pospucrio.silver.customers ALTER COLUMN customer_unique_id COMMENT 'Identificador do cliente (permite rastrear cliente recorrente em múltiplos pedidos).';
# MAGIC ALTER TABLE pospucrio.silver.customers ALTER COLUMN customer_zip_code_prefix COMMENT 'Primeiros 5 dígitos do CEP do cliente.';
# MAGIC ALTER TABLE pospucrio.silver.customers ALTER COLUMN customer_city COMMENT 'Cidade do endereço do cliente.';
# MAGIC ALTER TABLE pospucrio.silver.customers ALTER COLUMN customer_state COMMENT 'UF (sigla do estado) do endereço do cliente.';
# MAGIC
# MAGIC -- Colunas Silver - orders
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_id COMMENT 'Identificador único do pedido (chave primária).';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN customer_id COMMENT 'Chave estrangeira para pospucrio.silver.customers.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_status COMMENT 'Status do pedido: delivered, shipped, canceled, unavailable, invoiced, processing, created ou approved.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_purchase_timestamp COMMENT 'Data e hora da compra pelo cliente.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_approved_at COMMENT 'Data e hora da aprovação do pagamento.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_delivered_carrier_date COMMENT 'Data e hora em que o pedido foi entregue à transportadora.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_delivered_customer_date COMMENT 'Data e hora da entrega ao cliente.';
# MAGIC ALTER TABLE pospucrio.silver.orders ALTER COLUMN order_estimated_delivery_date COMMENT 'Data estimada de entrega informada ao cliente na compra.';
# MAGIC
# MAGIC -- Colunas Silver - order_items
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN order_id COMMENT 'Chave estrangeira para pospucrio.silver.orders.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN order_item_id COMMENT 'Número sequencial do item dentro do pedido, a partir de 1.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN product_id COMMENT 'Chave estrangeira para pospucrio.silver.products.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN seller_id COMMENT 'Chave estrangeira para pospucrio.silver.sellers.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN shipping_limit_date COMMENT 'Data limite para o vendedor despachar o item.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN price COMMENT 'Preço do item em reais, sem frete.';
# MAGIC ALTER TABLE pospucrio.silver.order_items ALTER COLUMN freight_value COMMENT 'Valor do frete do item em reais.';
# MAGIC
# MAGIC -- Colunas Silver - order_payments
# MAGIC ALTER TABLE pospucrio.silver.order_payments ALTER COLUMN order_id COMMENT 'Chave estrangeira para pospucrio.silver.orders.';
# MAGIC ALTER TABLE pospucrio.silver.order_payments ALTER COLUMN payment_sequential COMMENT 'Sequencial do pagamento dentro do pedido.';
# MAGIC ALTER TABLE pospucrio.silver.order_payments ALTER COLUMN payment_type COMMENT 'Tipo de pagamento: credit_card, boleto, voucher, debit_card ou not_defined.';
# MAGIC ALTER TABLE pospucrio.silver.order_payments ALTER COLUMN payment_installments COMMENT 'Número de parcelas do pagamento.';
# MAGIC ALTER TABLE pospucrio.silver.order_payments ALTER COLUMN payment_value COMMENT 'Valor do pagamento em reais.';
# MAGIC
# MAGIC -- Colunas Silver - order_reviews
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_id COMMENT 'Identificador único da avaliação.';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN order_id COMMENT 'Chave estrangeira para pospucrio.silver.orders.';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_score COMMENT 'Nota da avaliação, de 1 (pior) a 5 (melhor).';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_comment_title COMMENT 'Título do comentário da avaliação. Pode ser nulo.';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_comment_message COMMENT 'Texto do comentário da avaliação. Pode ser nulo.';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_creation_date COMMENT 'Data de criação da avaliação.';
# MAGIC ALTER TABLE pospucrio.silver.order_reviews ALTER COLUMN review_answer_timestamp COMMENT 'Data e hora da resposta à avaliação.';
# MAGIC
# MAGIC -- Colunas Silver - products (nomes já corrigidos: lenght → length)
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_id COMMENT 'Identificador único do produto (chave primária).';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_category_name COMMENT 'Nome da categoria do produto em português.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_name_length COMMENT 'Comprimento do nome do produto em caracteres.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_description_length COMMENT 'Comprimento da descrição do produto em caracteres.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_photos_qty COMMENT 'Quantidade de fotos do produto.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_weight_g COMMENT 'Peso do produto em gramas.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_length_cm COMMENT 'Comprimento do produto em centímetros.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_height_cm COMMENT 'Altura do produto em centímetros.';
# MAGIC ALTER TABLE pospucrio.silver.products ALTER COLUMN product_width_cm COMMENT 'Largura do produto em centímetros.';
# MAGIC
# MAGIC -- Colunas Silver - sellers
# MAGIC ALTER TABLE pospucrio.silver.sellers ALTER COLUMN seller_id COMMENT 'Identificador único do vendedor (chave primária).';
# MAGIC ALTER TABLE pospucrio.silver.sellers ALTER COLUMN seller_zip_code_prefix COMMENT 'Primeiros 5 dígitos do CEP do vendedor.';
# MAGIC ALTER TABLE pospucrio.silver.sellers ALTER COLUMN seller_city COMMENT 'Cidade do vendedor.';
# MAGIC ALTER TABLE pospucrio.silver.sellers ALTER COLUMN seller_state COMMENT 'UF (sigla do estado) do vendedor.';

# COMMAND ----------

# DBTITLE 1,5. Comentários nas tabelas Gold: pedidos
# MAGIC %md
# MAGIC ### 5.1 Catálogo de dados: gold.pedidos
# MAGIC
# MAGIC Registra no Unity Catalog a descrição da tabela e de cada coluna, com o domínio de valores e a origem. Essas descrições aparecem no Catalog Explorer para qualquer pessoa que abra a tabela.

# COMMAND ----------

# DBTITLE 1,5.2 Comentários: gold.pedidos
# MAGIC %sql
# MAGIC COMMENT ON TABLE pospucrio.gold.pedidos IS
# MAGIC 'Pedidos da Olist a partir de 2017, um por linha. Perspectiva do comprador: estado, valor pago, frete, prazo de entrega, forma e método de pagamento, nota da avaliação. Compras efetivadas são as de status delivered; o filtro é aplicado nas consultas. Origem: silver.orders, customers, order_items, order_payments e order_reviews.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN order_id         COMMENT 'Identificador do pedido. Chave da tabela. Hash hexadecimal de 32 caracteres. Origem: silver.orders.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN data_compra      COMMENT 'Data e hora da compra. A partir de 2017-01-01. Origem: silver.orders.order_purchase_timestamp.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN ano              COMMENT 'Ano da compra. Valores: 2017 e 2018. Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN mes              COMMENT 'Mês da compra, de 1 a 12. Derivado de data_compra. Usado para comparar os mesmos meses entre anos.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN semestre         COMMENT 'Semestre da compra: 1 (janeiro a junho) ou 2 (julho a dezembro). Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN trimestre        COMMENT 'Trimestre da compra, de 1 a 4. Derivado de data_compra. Trimestres completos: 2017-T1 a 2018-T2.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN estado_cliente   COMMENT 'UF do cliente, uma das 27 siglas. Origem: silver.customers.customer_state, via customer_id.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN status           COMMENT 'Status do pedido: delivered, shipped, canceled, unavailable, invoiced, processing, created ou approved. Apenas delivered conta como compra efetivada. Origem: silver.orders.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN valor_pago       COMMENT 'Soma de todos os pagamentos do pedido, em reais: produtos, frete, juros de parcelamento e vouchers. Maior ou igual a zero; nulo se o pedido não tem pagamento. Origem: silver.order_payments.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN frete_total      COMMENT 'Soma do frete dos itens do pedido, em reais. Maior ou igual a zero; nulo para pedidos sem itens registrados. Incluído também em valor_pago. Origem: silver.order_items.freight_value.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN dias_entrega     COMMENT 'Dias entre a compra e a entrega ao cliente. Nulo para pedidos não entregues ou sem data de entrega registrada. Derivado de silver.orders.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN forma_pagamento  COMMENT 'Valores: "à vista" ou "parcelado". Parcelado quando algum pagamento, exceto voucher, tem mais de uma parcela. Nulo para pedidos sem pagamento, com pagamento not_defined ou com parcelas inválidas na origem. Origem: silver.order_payments.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN metodo_principal COMMENT 'Valores: "cartão de crédito", "cartão de débito", "boleto" ou "voucher". Com voucher e outro meio, vale o outro; entre dois meios que não são voucher, o de maior valor. Nulo para not_defined ou sem pagamento. Origem: silver.order_payments.';
# MAGIC ALTER TABLE pospucrio.gold.pedidos ALTER COLUMN nota             COMMENT 'Nota da avaliação, de 1 a 5. Com mais de uma avaliação, vale a de resposta mais recente. Nulo se o pedido não foi avaliado. Origem: silver.order_reviews.';

# COMMAND ----------

# DBTITLE 1,5.3 Comentários nas tabelas Gold: itens
# MAGIC %md
# MAGIC ### 5.2 Catálogo de dados: gold.itens
# MAGIC
# MAGIC Registra no Unity Catalog a descrição da tabela e de cada coluna, com o domínio de valores e a origem.

# COMMAND ----------

# DBTITLE 1,5.4 Comentários: gold.itens
# MAGIC %sql
# MAGIC COMMENT ON TABLE pospucrio.gold.itens IS
# MAGIC 'Itens vendidos na Olist a partir de 2017, uma unidade por linha. Perspectiva do vendedor: estado do vendedor, categoria e preço. Vendas efetivadas são as de pedidos com status delivered; o filtro é aplicado nas consultas. Origem: silver.order_items, orders, customers, sellers e products.';
# MAGIC
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN order_id        COMMENT 'Identificador do pedido. Com order_item_id, forma a chave da tabela. Origem: silver.order_items.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN order_item_id   COMMENT 'Número sequencial do item dentro do pedido, a partir de 1. Com order_id, forma a chave. Origem: silver.order_items.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN data_compra     COMMENT 'Data e hora da compra do pedido. A partir de 2017-01-01. Origem: silver.orders.order_purchase_timestamp.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN ano             COMMENT 'Ano da compra. Valores: 2017 e 2018. Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN mes             COMMENT 'Mês da compra, de 1 a 12. Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN semestre        COMMENT 'Semestre da compra: 1 ou 2. Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN trimestre       COMMENT 'Trimestre da compra, de 1 a 4. Derivado de data_compra.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN estado_cliente  COMMENT 'UF de quem comprou, uma das 27 siglas. Origem: silver.customers, via pedido.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN estado_vendedor COMMENT 'UF de quem vendeu o item. 23 UFs presentes. Origem: silver.sellers.seller_state.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN categoria       COMMENT 'Categoria do produto em português, com espaços no lugar de sublinhados. "sem categoria" para produtos com cadastro incompleto. Origem: silver.products.product_category_name.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN preco           COMMENT 'Preço do item em reais, sem frete. Maior que zero; mediana de 74,99 e máximo de 6.735,00 reais. Origem: silver.order_items.price.';
# MAGIC ALTER TABLE pospucrio.gold.itens ALTER COLUMN status          COMMENT 'Status do pedido ao qual o item pertence. Apenas delivered conta como venda efetivada. Origem: silver.orders.order_status.';

# COMMAND ----------

# DBTITLE 1,5. Tags de governança
# MAGIC %sql
# MAGIC -- ============================================
# MAGIC -- 5. TAGS DE GOVERNANÇA
# MAGIC -- ============================================
# MAGIC -- Tags: camada, dominio, pii, origem, granularidade
# MAGIC
# MAGIC -- Bronze
# MAGIC ALTER TABLE pospucrio.bronze.olist_customers_dataset SET TAGS ('camada'='bronze', 'dominio'='clientes', 'pii'='sim', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_geolocation_dataset SET TAGS ('camada'='bronze', 'dominio'='geolocalizacao', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_items_dataset SET TAGS ('camada'='bronze', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_payments_dataset SET TAGS ('camada'='bronze', 'dominio'='pagamentos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_order_reviews_dataset SET TAGS ('camada'='bronze', 'dominio'='avaliacoes', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_orders_dataset SET TAGS ('camada'='bronze', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_products_dataset SET TAGS ('camada'='bronze', 'dominio'='produtos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.olist_sellers_dataset SET TAGS ('camada'='bronze', 'dominio'='vendedores', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.bronze.product_category_name_translation SET TAGS ('camada'='bronze', 'dominio'='produtos', 'pii'='nao', 'origem'='kaggle');
# MAGIC
# MAGIC -- Silver
# MAGIC ALTER TABLE pospucrio.silver.customers SET TAGS ('camada'='silver', 'dominio'='clientes', 'pii'='sim', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.order_items SET TAGS ('camada'='silver', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.order_payments SET TAGS ('camada'='silver', 'dominio'='pagamentos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.order_reviews SET TAGS ('camada'='silver', 'dominio'='avaliacoes', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.orders SET TAGS ('camada'='silver', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.products SET TAGS ('camada'='silver', 'dominio'='produtos', 'pii'='nao', 'origem'='kaggle');
# MAGIC ALTER TABLE pospucrio.silver.sellers SET TAGS ('camada'='silver', 'dominio'='vendedores', 'pii'='nao', 'origem'='kaggle');
# MAGIC
# MAGIC -- Gold
# MAGIC ALTER TABLE pospucrio.gold.pedidos SET TAGS ('camada'='gold', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle', 'granularidade'='um_pedido_por_linha');
# MAGIC ALTER TABLE pospucrio.gold.itens SET TAGS ('camada'='gold', 'dominio'='pedidos', 'pii'='nao', 'origem'='kaggle', 'granularidade'='um_item_por_linha');
# MAGIC
# MAGIC -- Schemas
# MAGIC ALTER SCHEMA pospucrio.bronze SET TAGS ('camada'='bronze');
# MAGIC ALTER SCHEMA pospucrio.silver SET TAGS ('camada'='silver');
# MAGIC ALTER SCHEMA pospucrio.gold SET TAGS ('camada'='gold');
# MAGIC
# MAGIC -- Volume
# MAGIC ALTER VOLUME pospucrio.bronze.raw SET TAGS ('camada'='bronze', 'origem'='kaggle', 'formato'='csv');

# COMMAND ----------

# DBTITLE 1,6. Validação final
# MAGIC %sql
# MAGIC -- ============================================
# MAGIC -- 6. VALIDAÇÃO FINAL
# MAGIC -- ============================================
# MAGIC
# MAGIC -- Schemas restantes
# MAGIC SELECT schema_name, comment
# MAGIC FROM pospucrio.information_schema.schemata
# MAGIC ORDER BY schema_name;
# MAGIC
# MAGIC -- Tags aplicadas
# MAGIC SELECT schema_name, table_name, tag_name, tag_value
# MAGIC FROM pospucrio.information_schema.table_tags
# MAGIC ORDER BY schema_name, table_name, tag_name;
# MAGIC
# MAGIC -- Tabelas e comentários
# MAGIC SELECT table_schema, table_name, comment
# MAGIC FROM pospucrio.information_schema.tables
# MAGIC WHERE table_schema NOT IN ('information_schema')
# MAGIC ORDER BY table_schema, table_name;
# MAGIC
# MAGIC -- Volumes
# MAGIC SELECT volume_schema, volume_name, comment
# MAGIC FROM pospucrio.information_schema.volumes
# MAGIC ORDER BY volume_schema, volume_name;

# COMMAND ----------

