import { inject } from '@angular/core';
import { Router, CanActivateFn, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  
  const expectedRole = route.data['role'];
  const currentRole = auth.currentUser()?.role;

  if (currentRole === expectedRole) {
    return true;
  }
  
  return router.parseUrl('/dashboard');
};
