from schemas import Bicycle, BicycleDetect

def run_tests():
    print("🔍 Testing Bicycle.getOne(id=1)")
    try:
        bicycle = Bicycle.getOne(1)
        print( bicycle)
    except Exception as e:
        print("❌ Bicycle.getOne failed:", e)

    print("\n🔍 Testing BicycleDetect.getOne(id=1)")
    try:
        detect = BicycleDetect.getOne(1)
        print( detect)
    except Exception as e:
        print("❌ BicycleDetect.getOne failed:", e)

    print("\n🔍 Testing BicycleDetect.getByBicycleId(bicycle_id=1)")
    try:
        detects = BicycleDetect.getByBicycleId(1)
        print(f"✅ {len(detects)} detects found:")
        for d in detects:
            print(" -", d)
    except Exception as e:
        print("❌ BicycleDetect.getByBicycleId failed:", e)

if __name__ == "__main__":
    run_tests()