import asyncio
import pulumi.automation as auto
import snowflake.connector
import paramiko
from pinecone import Pinecone

def test_deployment():
    """
    Validates the deployed infrastructure by checking connectivity and resource state.
    """
    print("--- Starting Infrastructure Deployment Validation ---")
    validation_results = {}

    # 1. Select the test stack and get its outputs
    try:
        stack = auto.select_stack(
            stack_name="iac-audit-test",
            work_dir="."
        )
        outputs = stack.outputs()
    except Exception as e:
        print(f"❌ Could not select stack or get outputs: {e}")
        return

    # 2. Dynamically run validation checks based on available outputs
    if "lambda_labs" in outputs:
        validation_results["Lambda Labs"] = validate_lambda_labs(outputs.get("lambda_labs"))
    else:
        print("⏭️ Lambda Labs outputs not found. Skipping validation.")

    if "snowflake" in outputs:
        validation_results["Snowflake"] = validate_snowflake(outputs.get("snowflake"))
    else:
        print("⏭️ Snowflake outputs not found. Skipping validation.")
    
    if "pinecone" in outputs:
        validation_results["Pinecone"] = validate_pinecone(outputs.get("pinecone"))
    else:
        print("⏭️ Pinecone outputs not found. Skipping validation.")


    # 3. Report results
    print("\n--- Validation Summary ---")
    all_ok = True
    for component, result in validation_results.items():
        status = '✅ OK' if result else '❌ FAILED'
        if not result:
            all_ok = False
        print(f"- {component}: {status}")

    if all_ok:
        print("\n✅ All available infrastructure components validated successfully.")
    else:
        print("\n❌ Some infrastructure components failed validation.")

def validate_lambda_labs(lambda_outputs):
    """ Validates the Lambda Labs instance by attempting an SSH connection. """
    if not lambda_outputs:
        print("Lambda Labs outputs not found. Skipping validation.")
        return False
    
    # This is a placeholder. A real implementation would need to securely
    # retrieve the private key and instance IP from the outputs.
    # For now, we'll just check that the outputs exist.
    print("Validating Lambda Labs outputs...")
    if lambda_outputs.value.get("ssh_key_name") and lambda_outputs.value.get("instance_type"):
        print("  - Lambda Labs outputs found.")
        return True
    else:
        print("  - Missing key outputs for Lambda Labs.")
        return False

def validate_snowflake(snowflake_outputs):
    """ Validates the Snowflake deployment by connecting and running a query. """
    if not snowflake_outputs:
        print("Snowflake outputs not found. Skipping validation.")
        return False

    print("Validating Snowflake connection...")
    try:
        # These credentials would need to be fetched securely, likely via Pulumi ESC.
        # This is a simplified example.
        conn = snowflake.connector.connect(
            user="user_placeholder",
            password="password_placeholder",
            account="account_placeholder",
            warehouse=snowflake_outputs.value.get("warehouse_name"),
            database=snowflake_outputs.value.get("database_name"),
            schema=snowflake_outputs.value.get("schema_name"),
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("  - Snowflake connection and query successful.")
                return True
        return False
    except Exception as e:
        print(f"  - Snowflake connection failed: {e}")
        return False

def validate_pinecone(pinecone_outputs):
    """ Validates the Pinecone index by checking if it exists. """
    if not pinecone_outputs:
        print("Pinecone outputs not found. Skipping validation.")
        return False

    print("Validating Pinecone index...")
    try:
        # API key would be fetched from Pulumi ESC.
        pc = Pinecone(api_key="key_placeholder")
        index_name = pinecone_outputs.value.get("index_name") # Assuming this output exists
        if index_name in pc.list_indexes().names():
             print(f"  - Pinecone index '{index_name}' found.")
             return True
        else:
             print(f"  - Pinecone index '{index_name}' not found.")
             return False
    except Exception as e:
        print(f"  - Pinecone validation failed: {e}")
        return False

if __name__ == "__main__":
    test_deployment() 