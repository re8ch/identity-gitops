# HyperSwitch retirement

HyperSwitch is retired from the active payments path. The reviewed retirement
removes its Deployment, Service, non-secret runtime ConfigMaps and public
HTTPRoutes through the existing identity-access release executor.

The `hyperswitch-superposition-local-key` PVC remains declared and protected.
External PostgreSQL data, Secrets and registry images are not deleted. The
original accepted authority-transfer payload remains checked in as immutable
audit evidence; production overlays remove the retired objects before bundle
compilation. A future reactivation requires a new signed pull request and a new
accepted release rather than replaying the retired inventory.
