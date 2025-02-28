class computed_property:
    """A property decorator that caches results based on dependent attributes."""
    
    def __init__(self, *dependencies):
        self.dependencies = set(dependencies)
        self.name = None
        self.fget = None
        self.fset = None
        self.fdel = None
        self.doc = None
        
    def __call__(self, fget):
        self.name = fget.__name__
        self.fget = fget
        self.doc = fget.__doc__
        return self
        
    def __get__(self, obj):
        if obj is None:
            return self
            
        # Create cache if it doesn't exist
        if not hasattr(obj, '_computed_cache'):
            obj._computed_cache = {}
        if not hasattr(obj, '_computed_deps'):
            obj._computed_deps = {}
            
        cache_key = self.name
        current_deps = self._get_dependency_values(obj)
        
        # Check if value needs to be recomputed
        if (cache_key not in obj._computed_cache or
            cache_key not in obj._computed_deps or
            current_deps != obj._computed_deps[cache_key]):
            
            # Compute new value and update cache
            value = self.fget(obj)
            obj._computed_cache[cache_key] = value
            obj._computed_deps[cache_key] = current_deps
            
        return obj._computed_cache[cache_key]
    
    def _get_dependency_values(self, obj):
        """Get current values of dependencies that exist on the object."""
        return tuple(
            (dep, getattr(obj, dep))
            for dep in self.dependencies
            if hasattr(obj, dep)
        )
    
    def setter(self, fset):
        self.fset = fset
        return self
        
    def deleter(self, fdel):
        self.fdel = fdel
        return self
        
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("Can't set attribute that is None")
        self.fset(obj, value)
        
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("Can't delete attribute that is None")
        self.fdel(obj)