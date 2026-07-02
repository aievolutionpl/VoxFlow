"""VoxFlow - Local Speech-to-Text Application
Usage: python -m voxflow.main
"""
import sys
import os


def main():
    """Main entry point for VoxFlow."""
    # Set environment for better compatibility
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    # Fix encoding for Windows consoles
    if sys.platform == "win32":
        if sys.stdout is not None:
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr is not None:
            sys.stderr.reconfigure(encoding='utf-8')

    # Handle --test mode
    if "--test" in sys.argv:
        print("🧪 VoxFlow Test Mode")
        print("Testing imports...")
        try:
            from voxflow.config import VoxFlowConfig
            print("  ✓ config")
            from voxflow.recorder import AudioRecorder
            print("  ✓ recorder")
            from voxflow.transcriber import VoxTranscriber
            print("  ✓ transcriber")
            from voxflow.hotkey_manager import HotkeyManager  # noqa: F401
            print("  ✓ hotkey_manager")
            from voxflow.tray import TrayManager  # noqa: F401
            print("  ✓ tray")
            from voxflow.app import VoxFlowApp  # noqa: F401
            print("  ✓ app")
            print("\n✅ All imports successful!")

            # Test audio devices
            devices = AudioRecorder.list_devices()
            print(f"\n🎤 Audio input devices ({len(devices)}):")
            for d in devices:
                print(f"  [{d['index']}] {d['name']}")

            # Test config
            config = VoxFlowConfig.load()
            print(f"\n⚙️ Config: model={config.model_size}, lang={config.language}")
            print(f"   Models dir: {VoxTranscriber.get_models_dir()}")

            print("\n🎉 VoxFlow is ready to use!")
            return 0

        except ImportError as e:
            print(f"\n❌ Import failed: {e}")
            print("Run: pip install -r requirements.txt")
            return 1

    # Normal launch
    try:
        from voxflow.app import VoxFlowApp  # noqa: F811
        app = VoxFlowApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ VoxFlow error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
