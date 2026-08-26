resource "aws_glue_catalog_table" "races" {
  name          = "races"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/${var.season}/races/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "season"
      type = "bigint"
    }

    columns {
      name = "round"
      type = "bigint"
    }

    columns {
      name = "race_name"
      type = "string"
    }

    columns {
      name = "date"
      type = "date"
    }

    columns {
      name = "circuit_id"
      type = "string"
    }

    columns {
      name = "circuit_name"
      type = "string"
    }

    columns {
      name = "city"
      type = "string"
    }

    columns {
      name = "country"
      type = "string"
    }

    columns {
      name = "latitude"
      type = "double"
    }

    columns {
      name = "longitude"
      type = "double"
    }
  }
}

resource "aws_glue_catalog_table" "drivers" {
  name          = "drivers"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/${var.season}/drivers/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "driver_id"
      type = "string"
    }

    columns {
      name = "permanent_number"
      type = "string"
    }

    columns {
      name = "code"
      type = "string"
    }

    columns {
      name = "first_name"
      type = "string"
    }

    columns {
      name = "last_name"
      type = "string"
    }

    columns {
      name = "date_of_birth"
      type = "date"
    }

    columns {
      name = "nationality"
      type = "string"
    }
  }
}

resource "aws_glue_catalog_table" "constructors" {
  name          = "constructors"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/${var.season}/constructors/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "constructor_id"
      type = "string"
    }

    columns {
      name = "name"
      type = "string"
    }

    columns {
      name = "nationality"
      type = "string"
    }
  }
}

resource "aws_glue_catalog_table" "results" {
  name          = "results"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/${var.season}/results/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "season"
      type = "bigint"
    }

    columns {
      name = "race_name"
      type = "string"
    }

    columns {
      name = "circuit_id"
      type = "string"
    }

    columns {
      name = "driver_id"
      type = "string"
    }

    columns {
      name = "constructor_id"
      type = "string"
    }

    columns {
      name = "number"
      type = "string"
    }

    columns {
      name = "position"
      type = "bigint"
    }

    columns {
      name = "position_text"
      type = "string"
    }

    columns {
      name = "points"
      type = "double"
    }

    columns {
      name = "grid"
      type = "bigint"
    }

    columns {
      name = "laps"
      type = "bigint"
    }

    columns {
      name = "status"
      type = "string"
    }

    columns {
      name = "time_millis"
      type = "bigint"
    }

    columns {
      name = "time"
      type = "string"
    }

    columns {
      name = "fastest_lap_rank"
      type = "bigint"
    }

    columns {
      name = "fastest_lap"
      type = "bigint"
    }

    columns {
      name = "fastest_lap_time"
      type = "string"
    }
  }

  partition_keys {
    name = "round"
    type = "bigint"
  }
}

resource "aws_glue_catalog_table" "sprint" {
  name          = "sprint"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/${var.season}/sprint/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "season"
      type = "bigint"
    }
    columns {
      name = "race_name"
      type = "string"
    }
    columns {
      name = "circuit_id"
      type = "string"
    }
    columns {
      name = "driver_id"
      type = "string"
    }
    columns {
      name = "constructor_id"
      type = "string"
    }
    columns {
      name = "number"
      type = "string"
    }
    columns {
      name = "position"
      type = "bigint"
    }
    columns {
      name = "position_text"
      type = "string"
    }
    columns {
      name = "points"
      type = "double"
    }
    columns {
      name = "grid"
      type = "bigint"
    }
    columns {
      name = "laps"
      type = "bigint"
    }
    columns {
      name = "status"
      type = "string"
    }
    columns {
      name = "time_millis"
      type = "bigint"
    }
    columns {
      name = "time"
      type = "string"
    }
    columns {
      name = "fastest_lap_rank"
      type = "bigint"
    }
    columns {
      name = "fastest_lap"
      type = "bigint"
    }
    columns {
      name = "fastest_lap_time"
      type = "string"
    }

    # round is the partition column, so it is not repeated here.
  }

  partition_keys {
    name = "round"
    type = "bigint"
  }
}

resource "aws_glue_catalog_table" "driver_standings" {
  name          = "driver_standings"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/driver_standings/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "position"
      type = "bigint"
    }
    columns {
      name = "position_text"
      type = "string"
    }
    columns {
      name = "points"
      type = "double"
    }
    columns {
      name = "wins"
      type = "bigint"
    }
    columns {
      name = "driver_id"
      type = "string"
    }
    columns {
      name = "permanent_number"
      type = "string"
    }
    columns {
      name = "code"
      type = "string"
    }
    columns {
      name = "first_name"
      type = "string"
    }
    columns {
      name = "last_name"
      type = "string"
    }
    columns {
      name = "date_of_birth"
      type = "date"
    }
    columns {
      name = "nationality"
      type = "string"
    }
    columns {
      name = "constructor_ids"
      type = "array<string>"
    }
    columns {
      name = "constructor_names"
      type = "array<string>"
    }
  }

  partition_keys {
    name = "season"
    type = "bigint"
  }
  partition_keys {
    name = "round"
    type = "bigint"
  }
}

resource "aws_glue_catalog_table" "constructor_standings" {
  name          = "constructor_standings"
  database_name = aws_athena_database.f1_data.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.f1_data.bucket}/data_collected/constructor_standings/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "position"
      type = "bigint"
    }
    columns {
      name = "position_text"
      type = "string"
    }
    columns {
      name = "points"
      type = "double"
    }
    columns {
      name = "wins"
      type = "bigint"
    }
    columns {
      name = "constructor_id"
      type = "string"
    }
    columns {
      name = "constructor_name"
      type = "string"
    }
    columns {
      name = "nationality"
      type = "string"
    }
  }

  partition_keys {
    name = "season"
    type = "bigint"
  }
  partition_keys {
    name = "round"
    type = "bigint"
  }
}
